# API de Simulação e Cadastro de Cartão

Esta API automatiza o processo de simulação e cadastro de cartão no sistema PixCard.

## Endpoint: Simular e Cadastrar
```http
POST /simular-e-cadastrar
```

Este endpoint realiza a simulação e cadastro do cliente em uma única operação, incluindo upload direto de documentos.

### Payload (multipart/form-data)

O endpoint aceita um formulário multipart com os seguintes campos:

1. **dados** (text/plain): JSON string com os dados do cadastro
2. **arquivo_rg_verso** (file): Arquivo do RG Verso
3. **arquivo_comprovante_endereco** (file): Comprovante de endereço
4. **arquivo_comprovante_renda** (file): Comprovante de renda

### Estrutura do JSON (campo 'dados')
```json
{
    "usuario": "string",
    "senha": "string",
    "rg": "string",
    "data_emissao_rg": "string",
    "orgao_emissor": "string",
    "uf_emissao": "string",
    "naturalidade": "string",
    "uf_naturalidade": "string",
    "sexo": "string",
    "estado_civil": "string",
    "nome_mae": "string",
    "cep": "string",
    "numero_log": "string",
    "numero": "string",
    "complemento": "string",
    "data_admissao": "string",
    "profissao": "string",
    "descricao_profissao": "string",
    "cargo": "string",
    "tipo_conta": "string",
    "banco": "string",
    "agencia": "string",
    "conta": "string",
    "digito": "string",
    "ddd": "string",
    "telefone": "string",
    "email": "string",
    "cpf": "string",
    "matricula": "string",
    "empregador": "string",
    "valor_margem": "string"
}
```

### Respostas

#### Sucesso (200 OK)
```json
{
    "status": "success",
    "message": "Simulação e cadastro realizados com sucesso"
}
```

#### Erro de Autenticação (401 Unauthorized)
```json
{
    "detail": "Erro ao fazer login"
}
```

#### Erro de Arquivo (500 Internal Server Error)
```json
{
    "detail": "Erro ao processar arquivo: [mensagem de erro]"
}
```

### Exemplo de Uso com curl

```bash
curl -X POST "http://localhost:8000/simular-e-cadastrar" \
     -H "Content-Type: multipart/form-data" \
     -F "dados={\"usuario\":\"NIVRIX.LUCASANDRADE\",\"senha\":\"12345\",\"rg\":\"162732\",\"data_emissao_rg\":\"01/01/2020\",\"orgao_emissor\":\"SSP\",\"uf_emissao\":\"SP\",\"naturalidade\":\"SAO PAULO\",\"uf_naturalidade\":\"SP\",\"sexo\":\"M\",\"estado_civil\":\"2\",\"nome_mae\":\"MARIA JOSE PAULA GOMES SILVA\",\"cep\":\"69311-114\",\"numero_log\":\"123\",\"numero\":\"123\",\"complemento\":\"\",\"data_admissao\":\"01/01/2020\",\"profissao\":\"\",\"descricao_profissao\":\"\",\"cargo\":\"\",\"tipo_conta\":\"1\",\"banco\":\"104\",\"agencia\":\"04263-3\",\"conta\":\"42886\",\"digito\":\"8\",\"ddd\":\"11\",\"telefone\":\"987654321\",\"email\":\"exemplo@email.com\",\"cpf\":\"637.250.882-68\",\"matricula\":\"0129843702\",\"empregador\":\"26\",\"valor_margem\":\"30\"}" \
     -F "arquivo_rg_verso=@documentos/cnh.jpg" \
     -F "arquivo_comprovante_endereco=@documentos/cch.jpg" \
     -F "arquivo_comprovante_renda=@documentos/residencia.jpg"
```

### Exemplo de Uso com Python

```python
import requests
import json

url = "http://localhost:8000/simular-e-cadastrar"

# Dados do cadastro
dados = {
    "usuario": "NIVRIX.LUCASANDRADE",
    "senha": "12345",
    # ... outros campos ...
}

# Arquivos para upload
files = {
    'arquivo_rg_verso': ('cnh.jpg', open('documentos/cnh.jpg', 'rb')),
    'arquivo_comprovante_endereco': ('cch.jpg', open('documentos/cch.jpg', 'rb')),
    'arquivo_comprovante_renda': ('residencia.jpg', open('documentos/residencia.jpg', 'rb'))
}

# Dados do formulário
data = {
    'dados': json.dumps(dados)
}

# Faz a requisição
response = requests.post(url, files=files, data=data)
print(response.json())
```

### Observações Importantes

1. **Formato das Datas**: Use o formato DD/MM/YYYY
2. **CPF**: Use o formato XXX.XXX.XXX-XX
3. **CEP**: Use o formato XXXXX-XXX
4. **Arquivos**:
   - Devem ser enviados como arquivos binários
   - Formatos aceitos: JPG, PNG, PDF
   - Tamanho máximo: 10MB por arquivo
5. **Tempo de Execução**: O processo pode levar alguns segundos para ser concluído
6. **Logs**: Em caso de erro, verifique os logs da API para mais detalhes

### Fluxo de Execução

1. Recebimento dos arquivos e dados
2. Login no sistema
3. Simulação do cartão
4. Preenchimento do formulário de cadastro
5. Upload de documentos
6. Aprovação do cadastro
7. Limpeza dos arquivos temporários

## Requisitos

- Python 3.8+
- Google Chrome
- Dependências Python (instaladas via pip)

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando a API

```bash
python api.py
```

A API estará disponível em `http://localhost:8000`

## Documentação Interativa

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Exemplo de Uso com curl

```bash
curl -X POST "http://localhost:8000/simular-e-cadastrar" \
     -H "Content-Type: multipart/form-data" \
     -F "dados={\"usuario\":\"NIVRIX.LUCASANDRADE\",\"senha\":\"12345\",\"rg\":\"162732\",\"data_emissao_rg\":\"01/01/2020\",\"orgao_emissor\":\"SSP\",\"uf_emissao\":\"SP\",\"naturalidade\":\"SAO PAULO\",\"uf_naturalidade\":\"SP\",\"sexo\":\"M\",\"estado_civil\":\"2\",\"nome_mae\":\"MARIA JOSE PAULA GOMES SILVA\",\"cep\":\"69311-114\",\"numero_log\":\"123\",\"numero\":\"123\",\"complemento\":\"\",\"data_admissao\":\"01/01/2020\",\"profissao\":\"\",\"descricao_profissao\":\"\",\"cargo\":\"\",\"tipo_conta\":\"1\",\"banco\":\"104\",\"agencia\":\"04263-3\",\"conta\":\"42886\",\"digito\":\"8\",\"ddd\":\"11\",\"telefone\":\"987654321\",\"email\":\"exemplo@email.com\",\"cpf\":\"637.250.882-68\",\"matricula\":\"0129843702\",\"empregador\":\"26\",\"valor_margem\":\"30\"}" \
     -F "arquivo_rg_verso=@documentos/cnh.jpg" \
     -F "arquivo_comprovante_endereco=@documentos/cch.jpg" \
     -F "arquivo_comprovante_renda=@documentos/residencia.jpg"
```

## Exemplo de Uso com Python

```python
import requests
import json

url = "http://localhost:8000/simular-e-cadastrar"

# Dados do cadastro
dados = {
    "usuario": "NIVRIX.LUCASANDRADE",
    "senha": "12345",
    # ... outros campos ...
}

# Arquivos para upload
files = {
    'arquivo_rg_verso': ('cnh.jpg', open('documentos/cnh.jpg', 'rb')),
    'arquivo_comprovante_endereco': ('cch.jpg', open('documentos/cch.jpg', 'rb')),
    'arquivo_comprovante_renda': ('residencia.jpg', open('documentos/residencia.jpg', 'rb'))
}

# Dados do formulário
data = {
    'dados': json.dumps(dados)
}

# Faz a requisição
response = requests.post(url, files=files, data=data)
print(response.json())
``` 