from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uvicorn
from scraper import iniciar_navegador, fazer_login, executar_acoes_simulacao, preencher_formulario_cadastro
from selenium import webdriver
import os
import logging
import requests
import tempfile
from urllib.parse import urlparse
import shutil
import boto3
from botocore.client import Config
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do DO Spaces
DO_SPACES_KEY = os.getenv('DO_SPACES_KEY')
DO_SPACES_SECRET = os.getenv('DO_SPACES_SECRET')
DO_SPACES_BUCKET = os.getenv('DO_SPACES_BUCKET')
DO_SPACES_FOLDER = os.getenv('DO_SPACES_FOLDER')
DO_SPACES_REGION = os.getenv('DO_SPACES_REGION')
DO_SPACES_ENDPOINT = os.getenv('DO_SPACES_ENDPOINT')

# Configuração do cliente DO Spaces
session = boto3.session.Session()
client = session.client('s3',
    region_name=DO_SPACES_REGION,
    endpoint_url=DO_SPACES_ENDPOINT,
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET,
    config=Config(s3={'addressing_style': 'virtual'})
)

app = FastAPI(title="Scraper API", description="API para automação de cadastro e simulação de cartão")

# Configuração do CORS
origins = [
    "http://localhost:3020",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3020",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "*"  # Permite todas as origens
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

class DadosSimulacao(BaseModel):
    cpf: str
    matricula: str
    empregador: str
    valor_margem: str
    tipo_produto: str = "1"

class DadosCadastroBase(BaseModel):
    # Dados de Login
    usuario: str
    senha: str
    
    # Dados de Documentação
    rg: str
    data_emissao_rg: str
    orgao_emissor: str
    uf_emissao: str
    
    # Dados Pessoais
    naturalidade: str
    uf_naturalidade: str
    sexo: str
    estado_civil: str
    nome_mae: str
    
    # Endereço
    cep: str
    numero_log: str
    numero: str
    complemento: str
    
    # Dados Profissionais
    data_admissao: str
    profissao: str
    descricao_profissao: str
    cargo: str
    
    # Dados Bancários
    tipo_conta: str
    banco: str
    agencia: str
    conta: str
    digito: str
    
    # Contato
    ddd: str
    telefone: str
    email: str
    
    # Dados da Simulação
    cpf: str
    matricula: str
    empregador: str
    valor_margem: str
    tipo_produto: str = "1"

def get_do_spaces_url(file_path: str) -> str:
    """Gera a URL completa para um arquivo no DO Spaces"""
    return f"{DO_SPACES_ENDPOINT}/{DO_SPACES_BUCKET}/{DO_SPACES_FOLDER}/{file_path}"

def download_from_do_spaces(file_path: str) -> str:
    """Download um arquivo do DO Spaces e retorna o caminho local temporário"""
    try:
        # Cria um arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_path)[1])
        
        # Log do caminho completo
        bucket = os.getenv('DO_SPACES_BUCKET')
        folder = os.getenv('DO_SPACES_FOLDER')
        full_path = f"{folder}/{file_path}"
        logger.info(f"Tentando baixar arquivo do DO Spaces: bucket={bucket}, path={full_path}")
        
        # Faz o download do arquivo
        client.download_file(
            bucket,
            full_path,
            temp_file.name
        )
        
        logger.info(f"Arquivo baixado com sucesso para {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo do DO Spaces {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao baixar arquivo do DO Spaces: {str(e)}")

def process_file_path(file_path: str) -> str:
    """Processa o caminho do arquivo, baixando se for uma URL ou arquivo do DO Spaces"""
    if file_path.startswith(('http://', 'https://')):
        logger.info(f"Baixando arquivo de {file_path}")
        return download_file(file_path)
    elif file_path.startswith('do://'):
        # Remove o prefixo 'do://' e baixa do DO Spaces
        do_path = file_path[5:]
        logger.info(f"Baixando arquivo do DO Spaces: {do_path}")
        return download_from_do_spaces(do_path)
    logger.info(f"Usando arquivo local: {file_path}")
    return file_path

def download_file(url: str) -> str:
    """Download um arquivo de uma URL e retorna o caminho local temporário"""
    try:
        # Cria um arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(urlparse(url).path)[1])
        
        # Faz o download do arquivo
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salva o arquivo
        with open(temp_file.name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return temp_file.name
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo de {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao baixar arquivo: {str(e)}")

async def save_upload_file(upload_file: UploadFile) -> str:
    """Salva um arquivo enviado e retorna o caminho temporário"""
    try:
        # Cria um arquivo temporário com a extensão correta
        suffix = os.path.splitext(upload_file.filename)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        # Salva o conteúdo do arquivo
        content = await upload_file.read()
        with open(temp_file.name, 'wb') as f:
            f.write(content)
            
        return temp_file.name
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo {upload_file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")

@app.post("/simular-cartao")
async def simular_cartao(dados: DadosSimulacao):
    try:
        logger.info("Iniciando simulação de cartão")
        logger.info(f"Dados recebidos: {dados.dict()}")
        
        driver = iniciar_navegador()
        url_inicial = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Simulacao/ICSimulacao"
        
        # Configura as variáveis de ambiente temporariamente
        os.environ['CPF'] = dados.cpf
        os.environ['MATRICULA'] = dados.matricula
        os.environ['EMPREGADOR'] = dados.empregador
        os.environ['VALOR_MARGEM'] = dados.valor_margem
        os.environ['TIPO_PRODUTO'] = dados.tipo_produto
        
        logger.info("Tentando fazer login")
        if fazer_login(driver, url_inicial):
            logger.info("Login realizado com sucesso")
            driver.get(url_inicial)
            logger.info("Iniciando simulação")
            if executar_acoes_simulacao(driver):
                logger.info("Simulação realizada com sucesso")
                return {"status": "success", "message": "Simulação realizada com sucesso"}
            else:
                logger.error("Erro ao executar simulação")
                raise HTTPException(status_code=500, detail="Erro ao executar simulação")
        else:
            logger.error("Erro ao fazer login")
            raise HTTPException(status_code=401, detail="Erro ao fazer login")
            
    except Exception as e:
        logger.error(f"Erro durante a simulação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'driver' in locals():
            logger.info("Fechando navegador")
            driver.quit()

@app.post("/cadastrar-cliente")
async def cadastrar_cliente(dados: DadosCadastroBase):
    try:
        logger.info("Iniciando cadastro de cliente")
        logger.info(f"Dados recebidos: {dados.dict()}")
        
        driver = iniciar_navegador()
        url_inicial = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Simulacao/ICSimulacao"
        
        # Configura todas as variáveis de ambiente
        for key, value in dados.dict().items():
            os.environ[key.upper()] = value
        
        logger.info("Tentando fazer login")
        if fazer_login(driver, url_inicial):
            logger.info("Login realizado com sucesso")
            logger.info("Iniciando preenchimento do formulário")
            if preencher_formulario_cadastro(driver):
                logger.info("Cadastro realizado com sucesso")
                return {"status": "success", "message": "Cadastro realizado com sucesso"}
            else:
                logger.error("Erro ao preencher formulário")
                raise HTTPException(status_code=500, detail="Erro ao preencher formulário")
        else:
            logger.error("Erro ao fazer login")
            raise HTTPException(status_code=401, detail="Erro ao fazer login")
            
    except Exception as e:
        logger.error(f"Erro durante o cadastro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'driver' in locals():
            logger.info("Fechando navegador")
            driver.quit()

@app.post("/simular-e-cadastrar")
async def simular_e_cadastrar(
    dados: str = Form(...),
    arquivo_rg_verso: UploadFile = File(...),
    arquivo_comprovante_endereco: UploadFile = File(...),
    arquivo_comprovante_renda: UploadFile = File(...)
):
    temp_files = []
    try:
        # Converte a string JSON para dicionário
        dados_dict = json.loads(dados)
        logger.info("Iniciando simulação e cadastro")
        logger.info(f"Dados recebidos: {dados_dict}")
        
        # Salva os arquivos enviados
        arquivo_rg_verso_path = await save_upload_file(arquivo_rg_verso)
        arquivo_comprovante_endereco_path = await save_upload_file(arquivo_comprovante_endereco)
        arquivo_comprovante_renda_path = await save_upload_file(arquivo_comprovante_renda)
        
        # Adiciona os arquivos à lista de temporários
        temp_files.extend([
            arquivo_rg_verso_path,
            arquivo_comprovante_endereco_path,
            arquivo_comprovante_renda_path
        ])
        
        # Atualiza o dicionário com os caminhos dos arquivos
        dados_dict['arquivo_rg_verso'] = arquivo_rg_verso_path
        dados_dict['arquivo_comprovante_endereco'] = arquivo_comprovante_endereco_path
        dados_dict['arquivo_comprovante_renda'] = arquivo_comprovante_renda_path
        
        driver = iniciar_navegador()
        url_inicial = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Simulacao/ICSimulacao"
        
        # Configura todas as variáveis de ambiente
        for key, value in dados_dict.items():
            os.environ[key.upper()] = value
        
        logger.info("Tentando fazer login")
        if fazer_login(driver, url_inicial):
            logger.info("Login realizado com sucesso")
            driver.get(url_inicial)
            logger.info("Iniciando simulação")
            if executar_acoes_simulacao(driver):
                logger.info("Simulação realizada com sucesso")
                logger.info("Iniciando preenchimento do formulário")
                if preencher_formulario_cadastro(driver):
                    logger.info("Cadastro realizado com sucesso")
                    return {"status": "success", "message": "Simulação e cadastro realizados com sucesso"}
                else:
                    logger.error("Erro ao preencher formulário")
                    raise HTTPException(status_code=500, detail="Erro ao preencher formulário")
            else:
                logger.error("Erro ao executar simulação")
                raise HTTPException(status_code=500, detail="Erro ao executar simulação")
        else:
            logger.error("Erro ao fazer login")
            raise HTTPException(status_code=401, detail="Erro ao fazer login")
            
    except Exception as e:
        logger.error(f"Erro durante simulação e cadastro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Limpa arquivos temporários
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
                logger.info(f"Arquivo temporário removido: {temp_file}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo temporário {temp_file}: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 