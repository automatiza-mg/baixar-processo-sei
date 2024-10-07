import sys
import os
from dotenv import load_dotenv
import time
from suds.client import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def consultar_procedimento(**kwargs):
    client = Client(kwargs['API_SEI_URL'])
    dict_call = {
        'SiglaSistema': kwargs['API_SEI_SISTEMA'],
        'IdentificacaoServico': kwargs['API_SEI_TOKEN'],
        'IdUnidade': kwargs['API_SEI_UNIDADE'],
        'ProtocoloProcedimento': kwargs['API_SEI_PROCESSO'],
        'SinRetornarAssuntos': 'S',
        'SinRetornarInteressados': 'S',
        'SinRetornarObservacoes': 'S',
        'SinRetornarAndamentoGeracao': 'S',
        'SinRetornarAndamentoConclusao': 'S',
        'SinRetornarUltimoAndamento': 'S',
        'SinRetornarUnidadesProcedimentoAberto': 'S',
        'SinRetornarProcedimentosRelacionados': 'S',
        'SinRetornarProcedimentosAnexados': 'S',
    }
    response = client.service.consultarProcedimento(**dict_call)
    return response

def driver_initiate(processo_url):
    # import ipdb; ipdb.set_trace(context=10)
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(processo_url)
    return driver

def download_documents(driver):
    # Select all documents
    documents = driver.find_element(By.ID, 'lnkInfraCheck')
    documents.click()
    # Download button click
    download = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div[1]/button[1]')
    download.click()
    time.sleep(10)

    return None

def orquestrador(**kwargs):
    processo = consultar_procedimento(**kwargs)
    processo_url = str(processo.LinkAcesso)
    driver = driver_initiate(processo_url)
    download_documents(driver)

if __name__ == '__main__':
    load_dotenv()
    data = {
        'API_SEI_URL': os.getenv('API_SEI_URL'),
        'API_SEI_TOKEN': os.getenv('API_SEI_TOKEN'),
        'API_SEI_SISTEMA': os.getenv('API_SEI_SISTEMA'),
        'API_SEI_UNIDADE': os.getenv('API_SEI_UNIDADE'),
        'API_SEI_PROCESSO': os.getenv('API_SEI_PROCESSO'),
    }
    orquestrador(**data)