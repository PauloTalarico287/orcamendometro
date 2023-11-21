import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import gspread
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe, set_with_dataframe

url = "http://dados.prefeitura.sp.gov.br/dataset/7c34e3cc-e978-4810-a834-f8172c6ef81d/resource/cf3e5d80-8976-4d14-b139-4c820d6e9d35/download/basedadosexecucao0823.xlsx"
response = requests.get(url)

# Verifique se a solicitação foi bem-sucedida
if response.status_code == 200:
    # Salve o conteúdo do arquivo em um arquivo local
    with open("basedadosexecucao0823.xlsx", "wb") as f:
        f.write(response.content)

    # Leia o arquivo Excel usando o pandas
    df = pd.read_excel("basedadosexecucao0823.xlsx")

    # Agora você pode trabalhar com os dados em 'df'
    print(df.head())

else:
    print("Erro ao baixar o arquivo:", response.status_code)

orcamento = pd.read_excel("basedadosexecucao0823.xlsx")
orc=orcamento[['Ds_Orgao','Ds_Programa', 'Ds_Projeto_Atividade', 'Vl_Orcado_Ano','Vl_Liquidado', 'Vl_Pago']]
Gastos=orc.groupby('Ds_Orgao')
investimento=Gastos.sum()
investimento.sort_values('Vl_Liquidado', ascending=False)
investimento = investimento.reset_index()
novos = ['Órgão', 'Valor orçado em 2023', 'Valor Liquidado', 'Valor Pago']
investimento.columns = novos
credentials_info = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS', default='{}'))
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=scope)
gc = gspread.authorize(credentials)

spreadsheet_key = os.getenv('GOOGLE_SHEETS_SPREADSHEET_KEY', default=os.getenv('GOOGLE_SHEETS_SPREADSHEET_KEY'))

investimento_por_sub=investimento[investimento['Órgão'].str.contains('Subprefeitura')]
pd.set_option('float_format', '{:.2f}'.format)
investimento_por_sub['Executado'] = investimento_por_sub['Valor Liquidado']/investimento_por_sub['Valor orçado em 2023']*100
investimento_por_sub.sort_values('Executado', ascending=False)
investimento_por_sub
planilha = gc.open_by_key(spreadsheet_key)
guia = planilha.worksheet("Subprefeituras")
data_to_append = investimento_por_sub.values.tolist()
data_to_append = [investimento_por_sub.columns.tolist()] + data_to_append

guia.clear()
guia.update(data_to_append, 2)
