from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
from dotenv import load_dotenv

# --- CONFIGURAÇÕES E CREDENCIAIS ---
# As credenciais ficam no arquivo .env (fora do Git). Veja .env.example.
load_dotenv()
EMAIL_DESKDATA = os.getenv("EMAIL_DESKDATA")
SENHA_DESKDATA = os.getenv("SENHA_DESKDATA")
if not EMAIL_DESKDATA or not SENHA_DESKDATA:
    raise SystemExit("❌ Defina EMAIL_DESKDATA e SENHA_DESKDATA no arquivo .env")

SIGLA_ESTADO_TO_NOME = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins"
}

# === 1. INICIAR DRIVER (CORRIGIDO) ===
def iniciar_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Tire o comentário se quiser rodar sem janela
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # AQUI ESTAVA O ERRO: Removido o ChromeDriverManager.
    # O Selenium agora usa o driver nativo do sistema.
    return webdriver.Chrome(service=Service(), options=chrome_options)

# === 2. LOGIN NO DESKDATA ===
def login_deskdata(driver):
    try:
        driver.get("https://deskdata.com.br/entrar/")
        
        campo_email = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "user_login"))
        )
        campo_email.clear()
        campo_email.send_keys(EMAIL_DESKDATA)

        campo_senha = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "user_pass"))
        )
        campo_senha.clear()
        campo_senha.send_keys(SENHA_DESKDATA)

        botao_entrar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "wp-submit"))
        )
        botao_entrar.click()
        
        # Espera carregar a página interna
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Consultar pessoas"))
        )
        print("✅ Login no Deskdata realizado com sucesso.")
        return True
    except Exception as e:
        print(f"❌ Falha no login do Deskdata: {e}")
        return False

# === 3. BUSCA NO DESKDATA ===
def buscar_telefone_deskdata(nome_socio, estado, driver):
    try:
        print(f"🔁 Buscando no Deskdata por: {nome_socio} ({estado})")
        driver.get("https://deskdata.com.br/pessoas/")

        # Preenchimento do formulário
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-id='key-select']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Nome']"))).click()

        campo_nome = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fullname")))
        campo_nome.clear()
        campo_nome.send_keys(nome_socio)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-id='key-extra-select']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Endereço']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-target='#address-modal']"))).click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "address-modal")))

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-id='state-modal']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='bs-select-3']//span[text()='{estado}']"))).click()
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "address-modal-submit"))).click()

        checkbox_telefones = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "phones_extended")))
        if not checkbox_telefones.is_selected():
            checkbox_telefones.click()

        try:
            botao_consultar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "search")))
            botao_consultar.click()
        except Exception:
            driver.execute_script("document.getElementById('search').click();")
        
        print("...Aguardando resultados...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "div-overflow-mobile"))
        )

        # Extração dos telefones
        xpath_celulares = "//tr[.//td[@class='w-label' and text()='Celular']]//a"
        elementos_de_celular = driver.find_elements(By.XPATH, xpath_celulares)
        celulares_encontrados = [elemento.text.strip() for elemento in elementos_de_celular]
        
        if celulares_encontrados:
            resultado = ', '.join(celulares_encontrados)
            print(f"✅ Celulares encontrados: {resultado}")
            return resultado
        else:
            print("❌ Nenhum número de 'Celular' encontrado na tabela.")
            return "Não encontrado"

    except Exception as e:
        if "TimeoutException" in str(type(e)):
             print("❌ Nenhum resultado encontrado (tempo esgotado).")
             return "Não encontrado (sem resultados)"
        print(f"❌ Erro na busca por '{nome_socio}': {e}")
        return "Erro na busca"

# === 4. PROGRAMA PRINCIPAL ===
def main():
    driver = iniciar_driver()

    try:
        df_input = pd.read_excel("entrada_nomes.xlsx")
        print("📄 Planilha 'entrada_nomes.xlsx' lida com sucesso.")
        
        # Remove espaços extras nos nomes das colunas
        df_input.columns = df_input.columns.str.strip()

    except FileNotFoundError:
        print("❌ Arquivo 'entrada_nomes.xlsx' não encontrado.")
        driver.quit()
        return

    # Login único
    if not login_deskdata(driver):
        print("❌ Login no DeskData falhou.")
        driver.quit()
        return

    resultados = []

    # Loop pelos nomes
    for index, row in df_input.iterrows():
        nome = str(row.get("Nome", "")).strip()
        estado_sigla = str(row.get("Estado", "")).strip().upper()

        if not nome or not estado_sigla:
            print(f"⚠️ Linha {index + 2} ignorada (falta Nome ou Estado).")
            continue

        print(f"\n--- Buscando: {nome} ({estado_sigla}) ---")

        estado_nome_completo = SIGLA_ESTADO_TO_NOME.get(estado_sigla)

        if not estado_nome_completo:
            print(f"⚠️ Sigla de estado '{estado_sigla}' inválida.")
            telefone = "Sigla inválida"
        else:
            telefone = buscar_telefone_deskdata(nome, estado_nome_completo, driver)

        resultados.append({
            "Nome": nome,
            "Estado": estado_sigla,
            "Telefone": telefone
        })

    # Salvar
    df_saida = pd.DataFrame(resultados)
    df_saida.to_excel("saida_telefones_por_nome.xlsx", index=False)
    print("\n✅ Busca finalizada! Arquivo 'saida_telefones_por_nome.xlsx' gerado.")

    driver.quit()

if __name__ == "__main__":
    main()