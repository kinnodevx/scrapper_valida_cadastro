from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import tempfile
import shutil
from typing import Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

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

@app.post("/simular-e-cadastrar")
async def simular_e_cadastrar(
    dados: str = Form(...),
    arquivo_rg_verso: UploadFile = File(...),
    arquivo_comprovante_endereco: UploadFile = File(...),
    arquivo_comprovante_renda: UploadFile = File(...)
):
    try:
        # Parse dos dados do formulário
        dados_dict = json.loads(dados)
        
        # Criar diretório temporário para os arquivos
        with tempfile.TemporaryDirectory() as temp_dir:
            # Salvar arquivos temporariamente
            arquivo_rg_path = os.path.join(temp_dir, arquivo_rg_verso.filename)
            arquivo_endereco_path = os.path.join(temp_dir, arquivo_comprovante_endereco.filename)
            arquivo_renda_path = os.path.join(temp_dir, arquivo_comprovante_renda.filename)
            
            # Salvar arquivos
            with open(arquivo_rg_path, "wb") as f:
                shutil.copyfileobj(arquivo_rg_verso.file, f)
            with open(arquivo_endereco_path, "wb") as f:
                shutil.copyfileobj(arquivo_comprovante_endereco.file, f)
            with open(arquivo_renda_path, "wb") as f:
                shutil.copyfileobj(arquivo_comprovante_renda.file, f)
            
            # Atualizar caminhos dos arquivos nos dados
            dados_dict["arquivo_rg_verso"] = arquivo_rg_path
            dados_dict["arquivo_comprovante_endereco"] = arquivo_endereco_path
            dados_dict["arquivo_comprovante_renda"] = arquivo_renda_path
            
            # Executar simulação e cadastro
            logger.info("Iniciando simulação e cadastro")
            # ... código existente de simulação e cadastro ...
            
            return {"status": "success", "message": "Simulação e cadastro realizados com sucesso"}
            
    except json.JSONDecodeError:
        logger.error("Erro ao decodificar JSON dos dados")
        raise HTTPException(status_code=400, detail="JSON inválido nos dados do formulário")
    except Exception as e:
        logger.error(f"Erro durante o processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar requisição: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 