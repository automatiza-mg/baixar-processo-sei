import os
from dotenv import load_dotenv
import time
from suds.client import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def consultar_procedimento(**kwargs):
    client = Client(kwargs['API_SEI_URL'])
    dict_call = {
        'SiglaSistema': kwargs['API_SEI_SISTEMA'],
        'IdentificacaoServico': kwargs['API_SEI_TOKEN'],
        'IdUnidade': kwargs['API_SEI_UNIDADE'],
        'ProtocoloProcedimento': kwargs['API_SEI_PROCESSO'],
        'SinRetornarAssuntos': 'N',
        'SinRetornarInteressados': 'N',
        'SinRetornarObservacoes': 'N',
        'SinRetornarAndamentoGeracao': 'N',
        'SinRetornarAndamentoConclusao': 'N',
        'SinRetornarUltimoAndamento': 'N',
        'SinRetornarUnidadesProcedimentoAberto': 'N',
        'SinRetornarProcedimentosRelacionados': 'N',
        'SinRetornarProcedimentosAnexados': 'N',
    }
    response = client.service.consultarProcedimento(**dict_call)
    # Para ver o envelope criado na última requisição
    # Ideal para montar o robô no Automate
    # print(response.last_sent())
    return response

def driver_initiate(processo_url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument("--headless=new")
    options.add_argument("window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(processo_url)
    return driver

def login(driver, **kwargs):
    user = driver.find_element(By.ID, 'txtUsuario')
    senha = driver.find_element(By.ID, 'pwdSenha')
    user.send_keys(kwargs['SEI_LOGIN'])
    senha.send_keys(kwargs['SEI_PWD'])
    acessar = driver.find_element(By.ID, 'Acessar')
    dropdown = Select(driver.find_element(By.ID,"selOrgao"))
    dropdown.select_by_visible_text(kwargs['SEI_ORGAO'])
    acessar.click()
    return None

def download_after_login(driver):
    # Locate iframe
    iframe = driver.find_element(By.ID, 'ifrVisualizacao')
    driver.switch_to.frame(iframe)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'divArvoreAcoes')))
    a_tags = driver.find_elements(By.TAG_NAME, 'a')
    a_tag = [a for a in a_tags if 'pdf' in a.get_property('href')][0]
    a_tag.click()
    botao_gerar = driver.find_element(By.NAME, 'btnGerar')
    botao_gerar.click()
    # import ipdb; ipdb.set_trace(context=10)
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.NAME, 'btnGerar')))
    time.sleep(10)
    return None

def download_without_login(driver):
    # Download button click
    documents = driver.find_element(By.ID, 'lnkInfraCheck')
    documents.click()
    download = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div[1]/button[1]')
    download.click()
    time.sleep(10)
    return None

def orquestrador(**kwargs):
    processo = consultar_procedimento(**kwargs)
    processo_url = str(processo.LinkAcesso)
    driver = driver_initiate(processo_url)
    if 'acao=procedimento_trabalhar' in processo_url:
        login(driver, **kwargs)
        download_after_login(driver)
    else:
        download_without_login(driver)
    return None

if __name__ == '__main__':
    load_dotenv()
    data = {
        'SEI_LOGIN': os.getenv('SEI_LOGIN'),
        'SEI_PWD': os.getenv('SEI_PWD'),
        'SEI_ORGAO': os.getenv('SEI_ORGAO'),
        'API_SEI_URL': os.getenv('API_SEI_URL'),
        'API_SEI_TOKEN': os.getenv('API_SEI_TOKEN'),
        'API_SEI_SISTEMA': os.getenv('API_SEI_SISTEMA'),
        'API_SEI_UNIDADE': os.getenv('API_SEI_UNIDADE'),
        'API_SEI_PROCESSO': os.getenv('API_SEI_PROCESSO'),
    }
    orquestrador(**data)
