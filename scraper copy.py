from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time

# Carrega as variáveis de ambiente
load_dotenv()

def iniciar_navegador():
    # Configura as opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--headless')  # Descomente para executar em modo headless
    
    # Inicializa o driver do Chrome
    service = Service()
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fazer_login(driver, url_inicial):
    try:
        # Acessa a URL inicial
        driver.get(url_inicial)
        
        # Aguarda até que a página de login seja carregada (caso seja redirecionado)
        wait = WebDriverWait(driver, 10)
        
        # Verifica se estamos na página de login
        if "ICLogin" in driver.current_url:
            # Aguarda o campo de usuário estar visível
            campo_usuario = wait.until(
                EC.presence_of_element_located((By.ID, "txtUsuario_CAMPO"))
            )
            
            # Aguarda o campo de senha estar visível
            campo_senha = wait.until(
                EC.presence_of_element_located((By.ID, "txtSenha_CAMPO"))
            )
            
            # Preenche os campos
            campo_usuario.send_keys(os.getenv('USUARIO'))
            campo_senha.send_keys(os.getenv('SENHA'))
            
            # Clica no botão de login
            botao_login = wait.until(
                EC.element_to_be_clickable((By.ID, "bbConfirmar"))
            )
            botao_login.click()
            
            # Aguarda um momento para o login ser processado
            time.sleep(3)
            
            # Diagnóstico: print da URL e screenshot
            print(f"URL após login: {driver.current_url}")
            driver.save_screenshot("screenshot_pos_login.png")
            
            return True
        else:
            print("Já estamos na página principal")
            return True
            
    except Exception as e:
        print(f"Erro durante o login: {str(e)}")
        return False

def executar_acoes_proposta(driver):
    try:
        wait = WebDriverWait(driver, 10)
        
        # Clica no botão de filtros
        botao_filtros = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-secondary[title='Filtros']"))
        )
        botao_filtros.click()
        time.sleep(1)  # Aguarda a animação do filtro
        
        # Encontra e preenche o campo de número da proposta
        campo_proposta = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_txtNumeroProposta_CAMPO"))
        )
        campo_proposta.clear()  # Limpa o campo
        campo_proposta.send_keys("28188")  # Digite o número da proposta
        time.sleep(1)  # Aguarda o preenchimento
        
        # Clica no botão de pesquisar
        botao_pesquisar = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_bbAtualizar"))
        )
        botao_pesquisar.click()
        
        # Aguarda a tabela carregar e clica no botão de detalhes
        time.sleep(2)  # Aguarda a tabela carregar
        botao_detalhes = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_grdProposta_ctl02_lnkDetalhesProposta"))
        )
        botao_detalhes.click()
        
        print("Ações na página de proposta executadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao executar ações na página de proposta: {str(e)}")
        return False

def main():
    url_inicial = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Proposta/ICPropostaCartao"
    url_destino = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Proposta/ICPropostaCartao"
    driver = iniciar_navegador()
    try:
        if fazer_login(driver, url_inicial):
            # Após login, acessar diretamente a página de proposta
            driver.get(url_destino)
            # Aguarda até estar na página correta ou timeout
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url.startswith(url_destino)
            )
            if driver.current_url.startswith(url_destino):
                print("Acesso à página de proposta realizado com sucesso!")
                # Executa as ações na página de proposta
                executar_acoes_proposta(driver)
            else:
                print(f"Não foi possível acessar a página de proposta. URL atual: {driver.current_url}")
            driver.save_screenshot("screenshot_proposta.png")
            # Não fecha o navegador, mantém aberto
            input("Pressione Enter para fechar o navegador...")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 