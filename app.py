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
orc=orcamento[['Ds_Orgao','Ds_Programa', 'Ds_Projeto_Atividade', 'Vl_Orcado_Ano','Vl_Liquidado']]
Gastos=orc.groupby('Ds_Orgao')
investimento=Gastos.sum()
investimento.sort_values('Vl_Liquidado', ascending=False)
investimento = investimento.reset_index()
novos = ['Órgão', 'Valor orçado em 2023', 'Valor Liquidado']
investimento.columns = novos
credentials_info = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS', default='{}'))
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=scope)
gc = gspread.authorize(credentials)

spreadsheet_key = os.getenv('GOOGLE_SHEETS_SPREADSHEET_KEY', default=os.getenv('GOOGLE_SHEETS_SPREADSHEET_KEY'))

#SUBPREFEITURAS
investimento_por_sub=investimento[investimento['Órgão'].str.contains('Subprefeitura')]
investimento_por_sub = investimento_por_sub.query('Órgão != "Secretaria Municipal das Subprefeituras"')
pd.set_option('float_format', '{:.2f}'.format)
investimento_por_sub
nomes_existentes = [
    "Subprefeitura Aricanduva/Formosa/Carrão",
    "Subprefeitura Butantã",
    "Subprefeitura Campo Limpo",
    "Subprefeitura Capela do Socorro",
    "Subprefeitura Casa Verde/Cachoeirinha",
    "Subprefeitura Cidade Ademar",
    "Subprefeitura Cidade Tiradentes",
    "Subprefeitura Ermelino Matarazzo",
    "Subprefeitura Freguesia/Brasilândia",
    "Subprefeitura Ipiranga",
    "Subprefeitura Itaim Paulista",
    "Subprefeitura Itaquera",
    "Subprefeitura Jabaquara",
    "Subprefeitura Jaçanã/Tremembé",
    "Subprefeitura Lapa",
    "Subprefeitura M'Boi Mirim",
    "Subprefeitura Mooca",
    "Subprefeitura Parelheiros",
    "Subprefeitura Penha",
    "Subprefeitura Perus/Anhanguera",
    "Subprefeitura Pinheiros",
    "Subprefeitura Pirituba/Jaraguá",
    "Subprefeitura Santana/Tucuruvi",
    "Subprefeitura Santo Amaro",
    "Subprefeitura Sapopemba",
    "Subprefeitura São Mateus",
    "Subprefeitura São Miguel Paulista",
    "Subprefeitura Sé",
    "Subprefeitura Vila Maria/Vila Guilherme",
    "Subprefeitura Vila Mariana",
    "Subprefeitura de Guaianases",
    "Subprefeitura de Vila Prudente"
]
novos_nomes = [
    "Aricanduva/Vila Formosa",
    "Butantã",
    "Campo Limpo",
    "Capela do Socorro",
    "Casa Verde",
    "Cidade Ademar",
    "Cidade Tiradentes",
    "Ermelino Matarazzo",
    "Freguesia do Ó/Brasilândia",
    "Ipiranga",
    "Itaim Paulista",
    "Itaquera",
    "Jabaquara",
    "Jaçanã/Tremembé",
    "Lapa",
    "M'Boi Mirim",
    "Mooca",
    "Parelheiros",
    "Penha",
    "Perus",
    "Pinheiros",
    "Pirituba/Jaraguá",
    "Santana/Tucuruvi",
    "Santo Amaro",
    "Sapopemba",
    "São Mateus",
    "São Miguel",
    "Sé",
    "Vila Maria/Vila Guilherme",
    "Vila Mariana",
    "Guaianases",
    "Vila Prudente"
]
mapeamento_nomes = dict(zip(nomes_existentes, novos_nomes))
investimento_por_sub['Órgão'] = investimento_por_sub['Órgão'].replace(mapeamento_nomes)
investimento_por_sub['Executado'] = investimento_por_sub['Valor Liquidado']/investimento_por_sub['Valor orçado em 2023']*100
investimento_por_sub.sort_values('Executado', ascending=False)
#investimento_por_sub.to_csv('Execução_Orçamento_Subprefeituras.csv')
investimento_por_sub
planilha = gc.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk")
guia = planilha.worksheet("Subprefeituras")
#data_to_append = investimento_por_sub.values.tolist()
#guia.update(data_to_append)
data_to_append = investimento_por_sub.values.tolist()
data_to_append = [investimento_por_sub.columns.tolist()] + data_to_append

guia.clear()
guia.update(data_to_append, 2)
#SECRETARIAS
investimento_por_sec = investimento[investimento['Órgão'].str.contains('Secretaria')] 
pd.set_option('float_format', '{:.2f}'.format)
investimento_por_sec['Executado'] = investimento_por_sec['Valor Liquidado']/investimento_por_sec['Valor orçado em 2023']*100
investimento_por_sec.sort_values('Executado', ascending=False)
planilha = gc.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk")
guia2 = planilha.worksheet("Secretarias")
data_to_append2 = investimento_por_sec.values.tolist()
data_to_append2 = [investimento_por_sec.columns.tolist()] + data_to_append2

guia2.clear()
guia2.update(data_to_append2, 2)

#OUTROS_ORGAOS
investimento_por_outros=investimento[~investimento['Órgão'].str.contains('Subprefeitura|Secretaria')]
pd.set_option('float_format', '{:.2f}'.format)
investimento_por_outros['Executado'] = investimento_por_outros['Valor Liquidado']/investimento_por_outros['Valor orçado em 2023']*100
investimento_por_outros.sort_values('Executado', ascending=False)
investimento_por_outros
planilha = gc.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk")
guia3 = planilha.worksheet("Outros")
#data_to_append = investimento_por_sub.values.tolist()
#guia.update(data_to_append)
data_to_append3 = investimento_por_outros.values.tolist()
data_to_append3 = [investimento_por_outros.columns.tolist()] + data_to_append3

guia3.clear()
guia3.update(data_to_append3, 2)

#TOTAL
total_por_coluna = investimento.sum()
pd.set_option('float_format', '{:.2f}'.format)
geral = pd.DataFrame({
    'Categoria': ['Total'],
    'Valor orçado em 2023': total_por_coluna['Valor orçado em 2023'],
    'Valor Liquidado': total_por_coluna['Valor Liquidado'],
    'Executado': [(total_por_coluna['Valor Liquidado'] / total_por_coluna['Valor orçado em 2023']) * 100],
})

planilha = gc.open_by_key("1Fwd76Zs_fyYWfJMhgROAHdvHLXYyt-uszcGtq5uHftk")
guia2 = planilha.worksheet("Geral")

# Atualizando a fórmula de execução na célula correspondente
linha_inicial = 2  # Pode ser ajustada conforme necessário
#guia2.update_acell('D1', '=(C{} / B{}) * 100'.format(linha_inicial, linha_inicial))

# Atualizando as células com os valores mais recentes
guia2.update('A2', geral['Categoria'].tolist()[0])  # Acessando o primeiro elemento da lista
guia2.update('B2', geral['Valor orçado em 2023'].tolist()[0])
guia2.update('C2', geral['Valor Liquidado'].tolist()[0])
guia2.update('D2', geral['Executado'].tolist()[0])
