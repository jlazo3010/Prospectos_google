import time
import json
import pandas as pd
import re
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager # Ya no lo usaremos directamente para la descarga

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.binary_location = "/usr/bin/chromium" # Mantenemos la ubicación del binario de Chromium

    # Obtiene la ruta absoluta al ChromeDriver en el repositorio
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver_bin", "chromedriver")

    # Asegúrate de que el ChromeDriver tenga permisos de ejecución
    os.chmod(chromedriver_path, 0o755)

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
    
def plus_code_to_coords(plus_code, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={plus_code}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
        return lat, lng
    else:
        return None, None

def scrapear_busqueda(busqueda: str, api_key: str) -> pd.DataFrame:
    driver = iniciar_driver()
    driver.get("https://www.google.com/maps")
    time.sleep(5)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(busqueda)
    search_box.send_keys(Keys.ENTER)
    time.sleep(10)

    for _ in range(20):
        try:
            scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
        except:
            break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all("div", class_="Nv2PK THOPZb CpccDe")
    results = []

    for idx, card in enumerate(cards):
        try:
            name = card.select_one("div.qBF1Pd").text
        except:
            name = ""

        try:
            link_tag = card.find("a", class_="hfpxzc")
            link = link_tag['href'] if link_tag else ""
        except:
            link = ""

        try:
            img_tag = card.find("img")
            image_url = img_tag['src'] if img_tag else ""
        except:
            image_url = ""

        full_address = ""
        phone = ""
        schedule = ""
        rating = ""
        reviews = ""
        top_comment = ""
        gallery_images = []
        plus_code = ""
        lat = lng = ""
        comentarios = []

        if link:
            try:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                time.sleep(6)

                profile_soup = BeautifulSoup(driver.page_source, 'html.parser')

                address_tag = profile_soup.find("button", {"data-item-id": "address"})
                if address_tag:
                    raw_address = address_tag.text.strip()
                    full_address = raw_address.replace('\ue0c8', '').strip()

                plus_tag = profile_soup.find("button", {"data-item-id": "oloc"})
                if plus_tag:
                    plus_code = plus_tag.text.strip()
                    lat, lng = plus_code_to_coords(plus_code, api_key)

                try:
                    phone_tags = profile_soup.find_all("button", class_="CsEnBe")
                    for tag in phone_tags:
                        if 'aria-label' in tag.attrs and "Teléfono" in tag['aria-label']:
                            phone = tag['aria-label'].replace("Teléfono: ", "").strip()
                            break
                except:
                    pass

                rating_tag = profile_soup.find("div", {"class": "F7nice"})
                if rating_tag:
                    rating = rating_tag.text.strip()

                review_count_tag = profile_soup.find("span", {"class": "UY7F9"})
                if review_count_tag:
                    reviews = review_count_tag.text.strip().strip("()")

                comentarios_contenedores = driver.find_elements(By.XPATH, '//div[@class="jftiEf fontBodyMedium "]')
                for contenedor in comentarios_contenedores:
                    try:
                        autor = contenedor.find_element(By.XPATH, './/div[@class="d4r55 "]').text
                    except:
                        autor = None
                    try:
                        perfil = contenedor.find_element(By.XPATH, './/div[@class="RfnDt "]').text
                    except:
                        perfil = None
                    try:
                        estrellas = len(contenedor.find_elements(By.XPATH, './/span[@class="hCCjke google-symbols NhBTye elGi1d"]'))
                    except:
                        estrellas = None
                    try:
                        fecha = contenedor.find_element(By.XPATH, './/span[@class="rsqaWe"]').text
                    except:
                        fecha = None
                    try:
                        texto = contenedor.find_element(By.XPATH, './/div[contains(@class,"MyEned")]/span').text
                    except:
                        texto = None
                    try:
                        likes = contenedor.find_element(By.XPATH, './/span[@class="pkWtMe"]').text
                    except:
                        likes = "0"

                    comentario = {
                        "autor": autor,
                        "perfil": perfil,
                        "estrellas": estrellas,
                        "fecha": fecha,
                        "texto": texto,
                        "likes": likes
                    }
                    comentarios.append(comentario)

                images = profile_soup.find_all("img")
                gallery_images = list(set(img['src'] for img in images if 'googleusercontent' in img.get('src', '') and img['src'] != image_url))

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"❌ Error al procesar {name}: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        results.append({
            "Nombre": name,
            "Link": link,
            "Imagen principal": image_url,
            "Galería de imágenes": ", ".join(gallery_images),
            "Dirección": full_address,
            "Teléfono": phone,
            "Calificación": rating,
            "Opiniones": reviews,
            "Comentarios": json.dumps(comentarios, ensure_ascii=False),
            "Plus Code": plus_code.replace("\uf186", ""),
            "Latitud": lat,
            "Longitud": lng,
            "Búsqueda": busqueda  # <- identificador de qué búsqueda es
        })

        print(f"✅ ({idx+1}/{len(cards)}) - {name}")

    driver.quit()
    return pd.DataFrame(results)
