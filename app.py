import pandas as pd
import gspread
from decouple import config
from oauth2client.service_account import ServiceAccountCredentials
import os

json_key_path = config('GOOGLE_SHEETS_CREDENTIALS', default=os.getenv('GOOGLE_SHEETS_CREDENTIALS'))
spreadsheet_key = config('GOOGLE_SHEETS_SPREADSHEET_KEY', default=os.getenv('GOOGLE_SHEETS_SPREADSHEET_KEY'))

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
client = gspread.authorize(creds)

def obter_dados_orcamento():
    url = "http://dados.prefeitura.sp.gov.br/dataset/7c34e3cc-e978-4810-a834-f8172c6ef81d/resource/cf3e5d80-8976-4d14-b139-4c820d6e9d35/download/basedadosexecucao0823.xlsx"
    df = pd.read_excel(url)
    return df

def atualizar_planilha_google():
    print("Iniciando atualização da planilha.")
    orcamento = obter_dados_orcamento()

    if orcamento is not None:
        print("Dados do orçamento obtidos com sucesso.")
        orc = orcamento[['Ds_Orgao', 'Ds_Programa', 'Ds_Projeto_Atividade', 'Vl_Orcado_Ano', 'Vl_Liquidado', 'Vl_Pago']]
        Gastos = orc.groupby('Ds_Orgao')
        investimento = Gastos.sum().reset_index()
        investimento.columns = ['Órgão', 'Valor orçado em 2023', 'Valor Liquidado', 'Valor Pago']
        investimento_por_sub = investimento[investimento['Órgão'].str.contains('Subprefeitura')]
        investimento_por_sub['Executado'] = investimento_por_sub['Valor Liquidado'] / investimento_por_sub['Valor orçado em 2023'] * 100
        investimento_por_sub = investimento_por_sub.sort_values('Executado', ascending=False)
        
        # Use as credenciais carregadas anteriormente
        planilha = client
        guia = planilha.open_by_key(spreadsheet_key).worksheet("Subprefeituras")
        guia.clear()
        guia.insert_rows(investimento_por_sub.values.tolist(), 2)

        # Realize a manipulação dos dados conforme necessário

if __name__ == "__main__":
    atualizar_planilha_google()
