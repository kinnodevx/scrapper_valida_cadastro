# Web Scraping PixCard

Este projeto realiza web scraping automatizado para o sistema PixCard.

## Requisitos

- Python 3.8 ou superior
- Google Chrome instalado

## Instalação

1. Clone este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

1. Edite o arquivo `.env` e adicione suas credenciais:
```
USUARIO=seu_usuario
SENHA=sua_senha
```

## Uso

Execute o script principal:
```bash
python scraper.py
```

## Funcionalidades

- Acessa automaticamente a URL inicial
- Se redirecionado para a página de login, realiza o login automaticamente
- Aguarda o carregamento dos elementos da página
- Trata possíveis erros durante o processo

## Observações

- O script está configurado para mostrar o navegador durante a execução
- Para executar em modo headless (sem interface gráfica), descomente a linha `chrome_options.add_argument('--headless')` no arquivo `scraper.py` 