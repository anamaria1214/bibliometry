from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def download_ieee(query="generative artificial intelligence", download_dir="data/raw"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": os.path.abspath(download_dir)}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 30)  # ⬅️ aumentamos a 30s por lo lenta que es IEEE

    try:
        # Abrir IEEE
        driver.get("https://ieeexplore.ieee.org/")
        print("[INFO] Página IEEE cargada")

        # Esperar que el buscador esté listo
        search_box = wait.until(
            EC.presence_of_element_located((By.ID, "globalSearchInput"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        print("[INFO] Búsqueda enviada")

        # Esperar a que aparezcan resultados
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.List-results-items")))
        print("[INFO] Resultados cargados")

        # Seleccionar todos los resultados
        select_all = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.List-results-actions input[type='checkbox']"))
        )
        driver.execute_script("arguments[0].click();", select_all)
        print("[INFO] Resultados seleccionados")

        # Botón Exportar
        export_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Export')]"))
        )
        export_button.click()
        print("[INFO] Menú Exportar abierto")

        # Opción BibTeX
        bibtex_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'BibTeX')]"))
        )
        bibtex_button.click()
        print("[INFO] Exportación en BibTeX iniciada")

        # Esperar la descarga
        time.sleep(10)
        print(f"[OK] Archivo descargado en {download_dir}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    download_ieee()
