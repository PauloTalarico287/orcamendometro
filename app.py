import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Carregue as credenciais do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("orcamendometro
/insperautomacaopaulo-092d64d2b0f1.json", scope)
client = gspread.authorize(creds)

def obter_dados_orcamento():
    url = "http://dados.prefeitura.sp.gov.br/dataset/7c34e3cc-e978-4810-a834-f8172c6ef81d/resource/cf3e5d80-8976-4d14-b139-4c820d6e9d35/download/basedadosexecucao0823.xlsx"
    df = pd.read_excel(url)
    return df

def atualizar_planilha_google():
    orcamento = obter_dados_orcamento()

    if orcamento is not None:
        # Realize a manipulação dos dados conforme necessário

        planilha = client.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk")
        guia = planilha.worksheet("Subprefeituras")
        guia.clear()
        guia.set_dataframe(orcamento, start="A2")

if __name__ == "__main__":
    atualizar_planilha_google()
