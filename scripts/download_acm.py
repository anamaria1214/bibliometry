from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from pathlib import Path
import shutil
import time
import os

def download_acm(start_page: int):
    """
    Inicia un navegador Firefox sin interfaz gráfica, navega a ACM Digital Library,
    acepta cookies, selecciona todos los resultados de la página y descarga las citas en formato BibTeX
    """
    download_dir = str(Path("downloads").resolve())
    output_dir = Path("data/raw")
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    firefox_options = Options()
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.dir", download_dir)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain, application/x-bibtex")
    firefox_options.set_preference("pdfjs.disabled", True)

    driver = webdriver.Firefox(options=firefox_options)
    wait = WebDriverWait(driver, 10)

    url = f"https://dl.acm.org/action/doSearch?AllField=generative+artificial+intelligence&startPage={start_page}&pageSize=50"
    driver.get(url)

    try:
        print("Waiting for cookie consent button...")
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        cookie_button.click()
        print("Cookies accepted")

        print("Selecting all results...")
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[name='markall']")
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(2)

        print("Opening export modal...")
        export_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.export-citation"))
        )
        driver.execute_script("arguments[0].click();", export_button)
        time.sleep(2)

        print("Clicking 'Download citation'...")
        download_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.download__btn[title='Download citation']"))
        )
        driver.execute_script("arguments[0].click();", download_btn)
        print("Download triggered")

        time.sleep(5)
        bib_files = sorted(Path(download_dir).glob("*.bib"), key=os.path.getmtime, reverse=True)
        if not bib_files:
            print("No .bib file found in downloads")

        latest_file = bib_files[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = output_dir / f"acm_scraped_{timestamp}.bib"
        shutil.move(str(latest_file), final_path)

        print(f"BibTeX file saved to: {final_path}")

        input("Press Enter to close the browser...")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        download_acm(1)
    except ValueError:
        print("Error con el inicio de la página")