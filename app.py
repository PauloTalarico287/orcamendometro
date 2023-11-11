import pandas as pd
import gspread
import os
from decouple import config
from oauth2client.service_account import ServiceAccountCredentials

# Carregue as credenciais do Google Sheets do ambiente
json_key_path = config('GOOGLE_SHEETS_JSON_KEY_PATH', default=os.getenv('GOOGLE_SHEETS_JSON_KEY_PATH'))
spreadsheet_key = config('GOOGLE_SHEETS_SPREADSHEET_KEY', default=os.getenv('GOOGLE_SHEETS_SPREADSHEET_KEY'))

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
client = gspread.authorize(creds)

# Carregue as credenciais do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("orcamendometro/insperautomacaopaulo-092d64d2b0f1.json", scope)
client = gspread.authorize(creds)

def obter_dados_orcamento():
    url = "http://dados.prefeitura.sp.gov.br/dataset/7c34e3cc-e978-4810-a834-f8172c6ef81d/resource/cf3e5d80-8976-4d14-b139-4c820d6e9d35/download/basedadosexecucao0823.xlsx"
    df = pd.read_excel(url)
    return df

def atualizar_planilha_google():
    orcamento = obter_dados_orcamento()

    if orcamento is not None:
        orc = orcamento[['Ds_Orgao', 'Ds_Programa', 'Ds_Projeto_Atividade', 'Vl_Orcado_Ano', 'Vl_Liquidado', 'Vl_Pago']]
        Gastos = orc.groupby('Ds_Orgao')
        investimento = Gastos.sum().reset_index()
        investimento.columns = ['Órgão', 'Valor orçado em 2023', 'Valor Liquidado', 'Valor Pago']
        investimento_por_sub = investimento[investimento['Órgão'].str.contains('Subprefeitura')]
        investimento_por_sub['Executado'] = investimento_por_sub['Valor Liquidado'] / investimento_por_sub['Valor orçado em 2023'] * 100
        investimento_por_sub = investimento_por_sub.sort_values('Executado', ascending=False)
        planilha = gspread.service_account(filename="credenciais.json")
        guia = planilha.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk").worksheet("Subprefeituras")
        guia.clear()
        guia.insert_rows(investimento_por_sub.values.tolist(), 2)

        # Realize a manipulação dos dados conforme necessário

if __name__ == "__main__":
    atualizar_planilha_google()
