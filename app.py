import pandas as pd
import requests
from bs4 import BeautifulSoup
import gspread
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from flask import Flask, request

SENDGRID_KEY = os.environ["SENDGRID_KEY"]
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as fobj:
  fobj.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)

@app.route("/")
def index():
  return "Quer saber mais do orçamento de SP?"

@app.route("/subprefeituras")
def subprefeituras():
  url = "http://dados.prefeitura.sp.gov.br/dataset/7c34e3cc-e978-4810-a834-f8172c6ef81d/resource/cf3e5d80-8976-4d14-b139-4c820d6e9d35/download/basedadosexecucao0823.xlsx"
  response = requests.get(url)
  if response.status_code == 200:
    with open("basedadosexecucao0823.xlsx", "wb") as f:
        f.write(response.content)
      df = pd.read_excel("basedadosexecucao0823.xlsx")
  else:
    print("Erro ao baixar o arquivo:", response.status_code)

orcamento = pd.read_excel("basedadosexecucao0823.xlsx")
orc=orcamento[['Ds_Orgao','Ds_Programa', 'Ds_Projeto_Atividade', 'Vl_Orcado_Ano','Vl_Liquidado', 'Vl_Pago']]
Gastos=orc.groupby('Ds_Orgao')
investimento=Gastos.sum()
investimento = investimento.reset_index()
novos = ['Órgão', 'Valor orçado em 2023', 'Valor Liquidado', 'Valor Pago']
investimento.columns = novos
print(investimento)
investimento_por_sub=investimento[investimento['Órgão'].str.contains('Subprefeitura')]
pd.set_option('float_format', '{:.2f}'.format)
investimento_por_sub['Executado'] = investimento_por_sub['Valor Liquidado']/investimento_por_sub['Valor orçado em 2023']*100
investimento_por_sub.sort_values('Executado', ascending=False)
#investimento_por_sub.to_csv('Execução_Orçamento_Subprefeituras.csv')
investimento_por_sub
planilha = client.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk")
guia = planilha.worksheet("Subprefeituras")
#data_to_append = investimento_por_sub.values.tolist()
#guia.update(data_to_append)
data_to_append = investimento_por_sub.values.tolist()
data_to_append = [investimento_por_sub.columns.tolist()] + data_to_append

guia.clear()
guia.update(data_to_append, 2) 
