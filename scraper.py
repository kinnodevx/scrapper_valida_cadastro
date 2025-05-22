from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
from selenium.webdriver.common.action_chains import ActionChains
import requests

# Carrega as variáveis de ambiente
load_dotenv()

def obter_endereco_cep(cep):
    try:
        # Remove caracteres não numéricos do CEP
        cep = ''.join(filter(str.isdigit, cep))
        
        # Consulta a API ViaCEP
        url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(url)
        
        if response.status_code == 200:
            dados = response.json()
            if not dados.get('erro'):
                return {
                    'logradouro': dados.get('logradouro', ''),
                    'bairro': dados.get('bairro', ''),
                    'uf': 'RR'  # Sempre RR
                }
        return None
    except Exception as e:
        print(f"Erro ao consultar CEP: {str(e)}")
        return None

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

def verificar_campos_obrigatorios(driver):
    try:
        wait = WebDriverWait(driver, 10)
        print("\n--- Verificando campos obrigatórios ---")
        
        # Verifica primeiro se os campos críticos estão preenchidos
        campos_criticos = {
            'CEP': "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtCEP_CAMPO",
            'Conta': "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtConta_CAMPO",
            'DV': "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtContaDV_CAMPO"
        }

        campos_vazios = []
        for nome, id_campo in campos_criticos.items():
            try:
                campo = wait.until(
                    EC.presence_of_element_located((By.ID, id_campo))
                )
                if not campo.get_attribute('value'):
                    campos_vazios.append(nome)
            except Exception as e:
                print(f"Erro ao verificar campo {nome}: {str(e)}")
                campos_vazios.append(nome)

        if campos_vazios:
            print(f"ERRO: Os seguintes campos obrigatórios estão vazios: {', '.join(campos_vazios)}")
            print("Não será possível prosseguir com o preenchimento.")
            return False

        print("Todos os campos críticos estão preenchidos. Prosseguindo com as verificações...")

        # Verifica e preenche Endereço
        campo_endereco = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtEndereco_CAMPO"))
        )
        if not campo_endereco.get_attribute('value'):
            print("Campo Endereço está vazio, preenchendo...")
            dados_endereco = obter_endereco_cep(os.getenv('CEP'))
            if dados_endereco:
                campo_endereco.clear()
                campo_endereco.send_keys(dados_endereco['logradouro'])
                print("Endereço preenchido")
            time.sleep(1)

        # Verifica e preenche Cidade
        campo_cidade = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtCidade_CAMPO"))
        )
        if not campo_cidade.get_attribute('value'):
            print("Campo Cidade está vazio, preenchendo...")
            campo_cidade.clear()
            campo_cidade.send_keys("Boa Vista")  # Cidade padrão para RR
            print("Cidade preenchida")
            time.sleep(1)

        # Verifica e preenche Data Admissão (valor fixo)
        campo_data_admissao = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtDataAdmissao_CAMPO"))
        )
        data_admissao = "20/03/2021"  # Valor fixo
        if not campo_data_admissao.get_attribute('value') or campo_data_admissao.get_attribute('value') != data_admissao:
            print("Campo Data Admissão está vazio ou incorreto, preenchendo...")
            campo_data_admissao.clear()
            campo_data_admissao.send_keys(data_admissao)
            # Força o evento blur para aplicar a máscara
            driver.execute_script("arguments[0].blur();", campo_data_admissao)
            print(f"Data Admissão preenchida: {data_admissao}")
            time.sleep(1)

        # Verifica e preenche Banco
        select_banco = Select(wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbBanco_CAMPO"))
        ))
        banco = os.getenv('BANCO')
        if not select_banco.first_selected_option.get_attribute('value') or select_banco.first_selected_option.get_attribute('value') != banco:
            print("Campo Banco está vazio ou incorreto, preenchendo...")
            select_banco.select_by_value(banco)
            print(f"Banco preenchido: {banco}")
            time.sleep(1)

        print("Verificação de campos obrigatórios concluída")
        return True

    except Exception as e:
        print(f"Erro ao verificar campos obrigatórios: {str(e)}")
        return False

def preencher_formulario_cadastro(driver):
    try:
        wait = WebDriverWait(driver, 10)
        print("\n=== Iniciando preenchimento do formulário ===")
        
        # Dados de Documentação
        print("\n--- Preenchendo Dados de Documentação ---")
        campo_rg = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtRG_CAMPO"))
        )
        campo_rg.clear()
        campo_rg.send_keys(os.getenv('RG'))
        print("RG preenchido")
        time.sleep(1)

        campo_data_emissao = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtDtEmissao_CAMPO"))
        )
        campo_data_emissao.clear()
        campo_data_emissao.send_keys(os.getenv('DATA_EMISSAO_RG'))
        print("Data de emissão preenchida")
        time.sleep(1)

        campo_orgao_emissor = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtLocalEmissao_CAMPO"))
        )
        campo_orgao_emissor.clear()
        campo_orgao_emissor.send_keys(os.getenv('ORGAO_EMISSOR'))
        print("Órgão emissor preenchido")
        time.sleep(1)

        # UF de Emissão do Documento
        select_uf_emissao = Select(wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbUFEmissao_CAMPO"))
        ))
        select_uf_emissao.select_by_value(os.getenv('UF_EMISSAO'))
        print("UF de emissão selecionada")
        time.sleep(1)

        # Dados Pessoais
        print("\n--- Preenchendo Dados Pessoais ---")
        campo_naturalidade = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtCidadeNatal_CAMPO"))
        )
        campo_naturalidade.clear()
        campo_naturalidade.send_keys(os.getenv('NATURALIDADE'))
        print("Naturalidade preenchida")
        time.sleep(1)

        # UF de Naturalidade
        select_uf_naturalidade = Select(wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbUFNatal_CAMPO"))
        ))
        select_uf_naturalidade.select_by_value(os.getenv('UF_NATURALIDADE'))
        print("UF de naturalidade selecionada")
        time.sleep(1)

        # Sexo
        sexo = os.getenv('SEXO')
        if sexo:
            select_sexo = Select(driver.find_element(By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbSexo_CAMPO"))
            # Mapeando o valor do sexo para o formato correto
            sexo_value = 'M' if sexo.upper() == 'MASCULINO' else 'F'
            select_sexo.select_by_value(sexo_value)
            print("Sexo selecionado")
        time.sleep(1)

        # Estado Civil
        estado_civil = os.getenv('ESTADO_CIVIL')
        if estado_civil:
            # Valores válidos: 1 (Casado), 2 (Solteiro), 3 (Divorciado), 4 (Viuvo), 5 (Desquitado)
            if estado_civil in ['1', '2', '3', '4', '5']:
                select_estado_civil = Select(wait.until(
                    EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbEstadoCivil_CAMPO"))
                ))
                select_estado_civil.select_by_value(estado_civil)
                print("Estado civil selecionado")
            else:
                print(f"Valor inválido para estado civil: {estado_civil}. Usando valor padrão '2' (Solteiro)")
                select_estado_civil = Select(wait.until(
                    EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbEstadoCivil_CAMPO"))
                ))
                select_estado_civil.select_by_value('2')
        time.sleep(1)

        # Filiação
        print("\n--- Preenchendo Filiação ---")
        campo_nome_mae = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtNomeMae_CAMPO"))
        )
        campo_nome_mae.clear()
        campo_nome_mae.send_keys(os.getenv('NOME_MAE'))
        print("Nome da mãe preenchido")
        time.sleep(1)

        # Endereço
        print("\n--- Preenchendo Endereço ---")
        # Preenche CEP
        cep = os.getenv('CEP')
        campo_cep = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtCEP_CAMPO"))
        )
        campo_cep.clear()
        campo_cep.send_keys(cep)
        print("CEP preenchido")
        time.sleep(2)  # Aguarda o preenchimento automático

        # Obtém dados do endereço via API
        dados_endereco = obter_endereco_cep(cep)
        if dados_endereco:
            # Preenche endereço
            campo_endereco = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtEndereco_CAMPO"))
            )
            campo_endereco.clear()
            campo_endereco.send_keys(dados_endereco['logradouro'])
            print("Endereço preenchido")
            time.sleep(1)

            # Preenche número
            campo_numero = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtEnderecoNR_CAMPO"))
            )
            campo_numero.clear()
            campo_numero.send_keys(os.getenv('NUMERO'))
            print("Número preenchido")
            time.sleep(1)

            # Preenche bairro
            campo_bairro = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtBairro_CAMPO"))
            )
            campo_bairro.clear()
            campo_bairro.send_keys(dados_endereco['bairro'])
            print("Bairro preenchido")
            time.sleep(1)

            # Preenche UF (sempre RR)
            select_uf = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_cbUF_CAMPO"))
            ))
            select_uf.select_by_value('RR')
            print("UF preenchida (RR)")
            time.sleep(1)

            # Preenche complemento
            campo_complemento = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucEnderecoResidencial_txtComplemento_CAMPO"))
            )
            campo_complemento.clear()
            campo_complemento.send_keys(os.getenv('COMPLEMENTO'))
            print("Complemento preenchido")
            time.sleep(1)
        else:
            print("Erro ao obter dados do endereço via CEP")

        # Dados Profissionais
        print("\n--- Preenchendo Dados Profissionais ---")
        campo_data_admissao = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtDataAdmissao_CAMPO"))
        )
        campo_data_admissao.clear()
        campo_data_admissao.send_keys(os.getenv('DATA_ADMISSAO'))
        print("Data de admissão preenchida")
        time.sleep(1)

        try:
            print("Tentando preencher profissão...")
            select_profissao = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbProfissao_CAMPO"))
            ))
            profissao = os.getenv('PROFISSAO')
            print(f"Valor da profissão: {profissao}")
            select_profissao.select_by_value(profissao)
            print("Profissão selecionada")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher profissão: {str(e)}")

        try:
            print("Tentando preencher descrição da profissão...")
            campo_descricao_profissao = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtProfissao_CAMPO"))
            )
            campo_descricao_profissao.clear()
            campo_descricao_profissao.send_keys(os.getenv('DESCRICAO_PROFISSAO'))
            print("Descrição da profissão preenchida")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher descrição da profissão: {str(e)}")

        try:
            print("Tentando preencher cargo...")
            campo_cargo = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtCargo_CAMPO"))
            )
            campo_cargo.clear()
            campo_cargo.send_keys(os.getenv('CARGO'))
            print("Cargo preenchido")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher cargo: {str(e)}")

        # Rendas
        print("\n--- Preenchendo Rendas ---")
        try:
            campo_renda = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtRenda_CAMPO"))
            )
            campo_renda.clear()
            campo_renda.send_keys(os.getenv('RENDA'))
            print("Renda preenchida")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher renda: {str(e)}")

        # Nº Benefício/Matrícula será preenchido automaticamente
        print("Número de benefício/matrícula será preenchido automaticamente")

        # Dados Bancários
        print("\n--- Preenchendo Dados Bancários ---")
        try:
            select_tipo_conta = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbTipoConta_CAMPO"))
            ))
            select_tipo_conta.select_by_value(os.getenv('TIPO_CONTA'))
            print("Tipo de conta selecionado")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao selecionar tipo de conta: {str(e)}")

        try:
            select_banco = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_cbBanco_CAMPO"))
            ))
            select_banco.select_by_value(os.getenv('BANCO'))
            print("Banco selecionado")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao selecionar banco: {str(e)}")

        try:
            campo_agencia = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtAgencia_CAMPO"))
            )
            campo_agencia.clear()
            campo_agencia.send_keys(os.getenv('AGENCIA'))
            print("Agência preenchida")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher agência: {str(e)}")

        try:
            campo_conta = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtConta_CAMPO"))
            )
            campo_conta.clear()
            campo_conta.send_keys(os.getenv('CONTA'))
            print("Conta preenchida")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher conta: {str(e)}")

        try:
            campo_digito = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtContaDV_CAMPO"))
            )
            campo_digito.clear()
            campo_digito.send_keys(os.getenv('DIGITO'))
            print("Dígito preenchido")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher dígito: {str(e)}")

        # Contato
        print("\n--- Preenchendo Contato ---")
        try:
            campo_ddd = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucTelefoneCelular_txtDDD_CAMPO"))
            )
            campo_ddd.clear()
            campo_ddd.send_keys(os.getenv('DDD'))
            print("DDD preenchido")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher DDD: {str(e)}")

        try:
            campo_telefone = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_ucTelefoneCelular_txtFone_CAMPO"))
            )
            campo_telefone.clear()
            campo_telefone.send_keys(os.getenv('TELEFONE'))
            print("Telefone preenchido")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher telefone: {str(e)}")

        try:
            campo_email = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_Container_AbaCliente_ucCadastroCliente_txtEmail_CAMPO"))
            )
            campo_email.clear()
            campo_email.send_keys(os.getenv('EMAIL'))
            print("Email preenchido")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao preencher email: {str(e)}")

        # Antes de clicar no botão Atualizar Cliente, verifica os campos obrigatórios
        print("\n--- Verificando campos obrigatórios antes de salvar ---")
        verificar_campos_obrigatorios(driver)

        # Clica no botão "Atualizar Cliente"
        print("\n--- Salvando cadastro ---")
        try:
            botao_atualizar = wait.until(
                EC.element_to_be_clickable((By.ID, "ctl00_Cph_Container_AbaCliente_bbGravar"))
            )
            botao_atualizar.click()
            print("Botão Atualizar Cliente clicado")
            time.sleep(2)  # Aguarda o processamento
        except Exception as e:
            print(f"Erro ao clicar no botão Atualizar Cliente: {str(e)}")

        # Upload de Documentos
        print("\n--- Upload de Documentos ---")
        try:
            # RG Verso
            print("Processando RG Verso...")
            select_tipo_doc_rg = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_ucAnexarDocumento1_cbTipoDocumento_CAMPO"))
            ))
            select_tipo_doc_rg.select_by_value("20")  # RG - Verso
            time.sleep(1)

            campo_arquivo_rg = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_ucAnexarDocumento1_fileUpload"))
            )
            campo_arquivo_rg.send_keys(os.path.abspath(os.getenv('ARQUIVO_RG_VERSO')))
            time.sleep(1)

            botao_importar_rg = wait.until(
                EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucAnexarDocumento1_bbEnviar"))
            )
            botao_importar_rg.click()
            print("RG Verso importado com sucesso")
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao importar RG Verso: {str(e)}")

        try:
            # Comprovante de Endereço
            print("Processando Comprovante de Endereço...")
            select_tipo_doc_endereco = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_ucAnexarDocumento1_cbTipoDocumento_CAMPO"))
            ))
            select_tipo_doc_endereco.select_by_value("4")  # Comprovante de Endereço
            time.sleep(1)

            campo_arquivo_endereco = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_ucAnexarDocumento1_fileUpload"))
            )
            campo_arquivo_endereco.send_keys(os.path.abspath(os.getenv('ARQUIVO_COMPROVANTE_ENDERECO')))
            time.sleep(1)

            botao_importar_endereco = wait.until(
                EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucAnexarDocumento1_bbEnviar"))
            )
            botao_importar_endereco.click()
            print("Comprovante de Endereço importado com sucesso")
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao importar Comprovante de Endereço: {str(e)}")

        try:
            # Comprovante de Renda
            print("Processando Comprovante de Renda...")
            select_tipo_doc_renda = Select(wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_ucAnexarDocumento1_cbTipoDocumento_CAMPO"))
            ))
            select_tipo_doc_renda.select_by_value("5")  # Comprovante de Renda
            time.sleep(1)

            campo_arquivo_renda = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_Cph_ucAnexarDocumento1_fileUpload"))
            )
            campo_arquivo_renda.send_keys(os.path.abspath(os.getenv('ARQUIVO_COMPROVANTE_RENDA')))
            time.sleep(1)

            botao_importar_renda = wait.until(
                EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucAnexarDocumento1_bbEnviar"))
            )
            botao_importar_renda.click()
            print("Comprovante de Renda importado com sucesso")
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao importar Comprovante de Renda: {str(e)}")

        # Clica no botão Aprovar
        print("\n--- Clicando no botão Aprovar ---")
        try:
            botao_aprovar = wait.until(
                EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucBotoesEsteira1_bbAprovar"))
            )
            botao_aprovar.click()
            print("Botão Aprovar clicado com sucesso!")
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao clicar no botão Aprovar: {str(e)}")
            driver.save_screenshot("erro_botao_aprovar.png")

        print("\n=== Formulário preenchido com sucesso! ===")
        return True

    except Exception as e:
        print(f"\nErro ao preencher formulário: {str(e)}")
        return False

def executar_acoes_simulacao(driver):
    try:
        wait = WebDriverWait(driver, 10)
        
        # Seleciona o primeiro ponto de venda
        select_pdv = Select(wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_cbLoja_CAMPO"))
        ))
        select_pdv.select_by_index(1)  # Seleciona a primeira opção (índice 1, pois 0 é o "-")
        time.sleep(1)
        
        # Seleciona o tipo de produto (Cartão Consignado ou Cartão Benefício)
        select_produto = Select(wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_cbTipoProduto_CAMPO"))
        ))
        tipo_produto = os.getenv('TIPO_PRODUTO', '1')  # 1 para Consignado, 4 para Benefício
        select_produto.select_by_value(tipo_produto)
        time.sleep(1)
        
        # Preenche o CPF (nome e data de nascimento serão preenchidos automaticamente)
        campo_cpf = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_txtCPF_CAMPO"))
        )
        campo_cpf.clear()
        campo_cpf.send_keys(os.getenv('CPF'))
        time.sleep(2)  # Aguarda um pouco mais para garantir que os campos sejam preenchidos automaticamente
        
        # Preenche a matrícula
        campo_matricula = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_txtNumeroBeneficio_CAMPO"))
        )
        campo_matricula.clear()
        campo_matricula.send_keys(os.getenv('MATRICULA'))
        time.sleep(1)
        
        # Seleciona o empregador
        select_empregador = Select(wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_cbEmpregador_CAMPO"))
        ))
        empregador = os.getenv('EMPREGADOR', '51')
        select_empregador.select_by_value(empregador)
        time.sleep(1)
        
        # Clica no botão de calcular margem
        botao_calcular = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_bbCalcularMargem"))
        )
        botao_calcular.click()
        time.sleep(2)  # Aguarda o cálculo da margem
        
        # Preenche o valor da margem
        campo_valor_margem = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_txtValorMargem_CAMPO"))
        )
        campo_valor_margem.clear()
        campo_valor_margem.send_keys(os.getenv('VALOR_MARGEM'))
        time.sleep(1)
        
        # Clica no botão OK (Atualizar Cálculo)
        botao_ok = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_lnkMargemOK"))
        )
        botao_ok.click()
        time.sleep(2)

        # Clica no botão "Exibir Tabelas"
        botao_exibir_tabelas = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_bbSimularConsignado"))
        )
        botao_exibir_tabelas.click()
        time.sleep(2)

        # Clica no botão de selecionar tabela (primeira opção)
        botao_selecionar_tabela = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_gridTabelas_ctl02_lnkDetalhes"))
        )
        botao_selecionar_tabela.click()
        time.sleep(2)

        # Clica no botão "Simular Saque"
        botao_simular_saque = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_bbSimularSaque"))
        )
        botao_simular_saque.click()
        time.sleep(2)

        # Clica no botão "Solicitar Proposta"
        botao_solicitar_proposta = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_bbSolicitarProposta"))
        )
        botao_solicitar_proposta.click()
        time.sleep(2)

        # Clica no botão "Sim"
        botao_sim = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_bbContinuarSim"))
        )
        botao_sim.click()
        print("Botão Sim clicado")
        time.sleep(3)  # Aumenta o tempo de espera após clicar em Sim

        # Clica no botão "OK"
        print("Tentando clicar no botão OK...")
        try:
            # Tenta localizar o botão de diferentes formas
            botao_ok = None
            try:
                botao_ok = wait.until(
                    EC.element_to_be_clickable((By.ID, "ctl00_Cph_ucSimulacaoCartaoConsignado_bbIniciarEsteira"))
                )
            except:
                try:
                    botao_ok = driver.find_element(By.CSS_SELECTOR, "a#ctl00_Cph_ucSimulacaoCartaoConsignado_bbIniciarEsteira.btn.btn-success")
                except:
                    botao_ok = driver.find_element(By.XPATH, "//a[contains(@id, 'bbIniciarEsteira')]")

            if botao_ok:
                # Tenta clicar de diferentes formas
                try:
                    botao_ok.click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", botao_ok)
                    except:
                        actions = ActionChains(driver)
                        actions.move_to_element(botao_ok).click().perform()
                
                print("Botão OK clicado com sucesso")
                time.sleep(3)  # Aguarda após o clique
            else:
                print("Botão OK não encontrado")
                driver.save_screenshot("erro_botao_ok.png")
        except Exception as e:
            print(f"Erro ao clicar no botão OK: {str(e)}")
            driver.save_screenshot("erro_botao_ok.png")

        # Prossegue com o preenchimento do formulário
        print("\n--- Iniciando preenchimento do formulário ---")
        preencher_formulario_cadastro(driver)
        
        print("Ações na página de simulação executadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao executar ações na página de simulação: {str(e)}")
        return False

def main():
    url_inicial = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Simulacao/ICSimulacao"
    url_destino = "https://pixcard.banksofttecnologia.com.br/AppCartao/Pages/Simulacao/ICSimulacao"
    driver = iniciar_navegador()
    try:
        if fazer_login(driver, url_inicial):
            # Após login, acessar diretamente a página de simulação
            driver.get(url_destino)
            # Aguarda até estar na página correta ou timeout
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url.startswith(url_destino)
            )
            if driver.current_url.startswith(url_destino):
                print("Acesso à página de simulação realizado com sucesso!")
                # Executa as ações na página de simulação
                executar_acoes_simulacao(driver)
            else:
                print(f"Não foi possível acessar a página de simulação. URL atual: {driver.current_url}")
            driver.save_screenshot("screenshot_simulacao.png")
            # Não fecha o navegador, mantém aberto
            input("Pressione Enter para fechar o navegador...")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 