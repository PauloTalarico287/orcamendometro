import pandas as pd
import requests
import gspread
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from flask import Flask, request
import os  # Importar a biblioteca os para acessar variáveis de ambiente

app = Flask(__name__)

# Obter as chaves de ambiente diretamente
SENDGRID_KEY = os.environ.get("SENDGRID_KEY")
GOOGLE_SHEETS_CREDENTIALS = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

def obter_dados_orcamento():
    url = "http://dados.prefeitura.sp.gov.br/dataset/7c34e3cc-e978-4810-a834-f8172c6ef81d/resource/cf3e5d80-8976-4d14-b139-4c820d6e9d35/download/basedadosexecucao0823.xlsx"
    response = requests.get(url)
    if response.status_code == 200:
        with open("basedadosexecucao0823.xlsx", "wb") as f:
            f.write(response.content)
        return pd.read_excel("basedadosexecucao0823.xlsx")
    else:
        print("Erro ao baixar o arquivo:", response.status_code)
        return None

@app.route("/")
def index():
    return "Quer saber mais do orçamento de SP?"

@app.route("/subprefeituras")
def subprefeituras():
    orcamento = obter_dados_orcamento()

    if orcamento is not None:
        orc = orcamento[['Ds_Orgao', 'Ds_Programa', 'Ds_Projeto_Atividade', 'Vl_Orcado_Ano', 'Vl_Liquidado', 'Vl_Pago']]
        Gastos = orc.groupby('Ds_Orgao')
        investimento = Gastos.sum().reset_index()
        investimento.columns = ['Órgão', 'Valor orçado em 2023', 'Valor Liquidado', 'Valor Pago']

        investimento_por_sub = investimento[investimento['Órgão'].str.contains('Subprefeitura')]
        investimento_por_sub['Executado'] = investimento_por_sub['Valor Liquidado'] / investimento_por_sub['Valor orçado em 2023'] * 100
        investimento_por_sub = investimento_por_sub.sort_values('Executado', ascending=False)

        # Salvar os dados em uma planilha do Google Sheets
        planilha = gspread.service_account(filename="credenciais.json")
        guia = planilha.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk").worksheet("Subprefeituras")
        guia.clear()
        guia.insert_rows(investimento_por_sub.values.tolist(), 2)

    return "Novos dados atualizados"

if __name__ == '__main__':
    app.run()
