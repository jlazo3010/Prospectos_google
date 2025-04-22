import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver_bin", "chromedriver")
    os.chmod(chromedriver_path, 0o755)
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

st.title("🧪 Test básico de carga de Google Maps")

if st.button("Probar carga de Google Maps"):
    try:
        st.write("⏳ Iniciando navegador...")
        driver = iniciar_driver()
        st.write("✅ Navegador iniciado")

        driver.get("https://www.google.com/maps")
        time.sleep(10)

        st.write("✅ Google Maps cargado (probablemente)")
        page_title = driver.title
        st.write(f"Título de la página: {page_title}")

        driver.quit()
    except Exception as e:
        st.error(f"❌ Error al cargar Google Maps: {e}")
