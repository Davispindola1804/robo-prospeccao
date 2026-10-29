
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

# Login Deskdata — credenciais lidas do arquivo .env (fora do Git). Veja .env.example.
load_dotenv()
EMAIL = os.getenv("EMAIL_DESKDATA")
SENHA = os.getenv("SENHA_DESKDATA")
if not EMAIL or not SENHA:
    raise SystemExit("❌ Defina EMAIL_DESKDATA e SENHA_DESKDATA no arquivo .env")

ARQUIVO_EXCEL = "entrada_dados.xlsx"
ARQUIVO_SAIDA = "saida_dados.xlsx"

def iniciar_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login_deskdata(driver):
    driver.get("https://deskdata.com.br/entrar/?redirect_to=https%3A%2F%2Fdeskdata.com.br%2F%2Fpessoas%2F")
    time.sleep(3)
    driver.find_element(By.ID, "user_login").send_keys(EMAIL)
    driver.find_element(By.ID, "user_pass").send_keys(SENHA)
    driver.find_element(By.ID, "wp-submit").click()
    time.sleep(5)

def buscar_telefone_deskdata(driver, nome, estado):
    if not nome:
        return ""
    driver.get("https://deskdata.com.br/pessoas")
    time.sleep(3)
    campo_nome = driver.find_element(By.ID, "form-field-nome")
    campo_nome.clear()
    campo_nome.send_keys(nome)
    campo_estado = driver.find_element(By.ID, "form-field-estado")
    campo_estado.clear()
    campo_estado.send_keys(estado)
    campo_estado.send_keys(Keys.RETURN)
    time.sleep(5)
    try:
        telefone = driver.find_element(By.XPATH, "//td[contains(text(),'Telefone')]/following-sibling::td").text.strip()
        return telefone
    except:
        return ""

def extrair_socios(driver):
    try:
        print("🔍 Extraindo sócios...")
        h2_element = driver.find_element(By.XPATH, "//h2[contains(text(),'Quadro de Sócios e Administradores')]")
        p_element = h2_element.find_element(By.XPATH, "following-sibling::p[1]")
        raw_html = p_element.get_attribute('innerHTML')
        socios = [s.strip() for s in raw_html.split('<br>') if s.strip()]
        print(f"👥 Sócios encontrados: {socios}")
        return socios
    except Exception as e:
        print(f"❌ Erro ao extrair sócios: {e}")
        return []

def extrair_estado(driver):
    try:
        print("📍 Extraindo estado...")
        h2_element = driver.find_element(By.XPATH, "//h2[contains(text(),'Localização')]")
        table = h2_element.find_element(By.XPATH, "following-sibling::table[1]")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            th = row.find_element(By.TAG_NAME, "th").text.strip()
            if "Estado" in th:
                estado = row.find_element(By.TAG_NAME, "td").text.strip()
                print(f"🏷️ Estado encontrado: {estado}")
                return estado
        return ""
    except Exception as e:
        print(f"❌ Erro ao extrair estado: {e}")
        return ""

def main():
    driver = iniciar_driver()
    login_deskdata(driver)
    print("📥 Lendo planilha de entrada...")
    dados = pd.read_excel(ARQUIVO_EXCEL)
    resultados = []
    for index, row in dados.iterrows():
        cnpj = str(row['CNPJ']).zfill(14).replace(".", "").replace("/", "").replace("-", "")
        print(f"🔍 Buscando dados para CNPJ: {cnpj}...")
        try:
            driver.get(f"https://cnpj.biz/{cnpj}")
            time.sleep(5)
            socios = extrair_socios(driver)
            estado = extrair_estado(driver)
            nome_socio = socios[0] if socios else ""
            telefone = buscar_telefone_deskdata(driver, nome_socio, estado)
        except Exception as e:
            print(f"⚠️ Não foi possível extrair dados para o CNPJ {cnpj}: {e}")
            telefone = ""
        resultados.append({
            "CNPJ": row["CNPJ"],
            "Razão Social": row.get("Razão Social", ""),
            "Telefone": telefone
        })
    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_excel(ARQUIVO_SAIDA, index=False)
    print(f"✅ Busca finalizada! Resultados salvos em {ARQUIVO_SAIDA}")
    driver.quit()

if __name__ == "__main__":
    main()
