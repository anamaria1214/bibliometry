from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path
import time
import os

def scrape_ieee_bibtex(page: int, playwright_page, download_dir: Path, output_dir: Path):
    """
    Navegar a IEEE Digital Library, aceptar cookies, seleccionar todos los resultados,
    y descargar citaciones en formato BibTeX
    """
    
    # URL con todos los parámetros (igual que tu código Selenium)
    url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=generative%20artificial%20intelligence&highlight=true&returnType=SEARCH&matchPubs=true&rowsPerPage=100&pageNumber={page}&returnFacets=ALL"
    
    print(f"Navegando a página {page}...")
    playwright_page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    
    try:
        # Aceptar cookies (solo en la primera página)
        if page == 1:
            print("Esperando para aceptar las cookies...")
            try:
                cookie_button = playwright_page.locator("button.osano-cm-accept-all.osano-cm-buttons__button.osano-cm-button.osano-cm-button--type_accept")
                cookie_button.wait_for(state="visible", timeout=10000)
                cookie_button.click()
                print("Cookies aceptadas")
                time.sleep(2)
            except:
                print("No se encontró banner de cookies o ya fue aceptado")
        
        # Seleccionar todos los resultados
        print("Seleccionando todos los resultados...")
        select_all_checkbox = playwright_page.locator("input.xpl-checkbox-default.results-actions-selectall-checkbox")
        select_all_checkbox.wait_for(state="visible", timeout=10000)
        select_all_checkbox.click()
        time.sleep(2)
        print("✓ Todos los resultados seleccionados")
        
        # Abrir el modal de exportación
        print("Abriendo el modal de exportación...")
        export_button = playwright_page.locator("button.xpl-btn-primary:has-text('Export')")
        export_button.wait_for(state="visible", timeout=10000)
        export_button.click()
        time.sleep(2)
        print("✓ Modal de exportación abierto")
        
        # Hacer clic en "Citations"
        print("Accediendo al modal de 'Citations'...")
        citations_button = playwright_page.locator("a.nav-link:has-text('Citations')")
        citations_button.wait_for(state="visible", timeout=10000)
        citations_button.click()
        time.sleep(2)
        print("✓ Pestaña Citations seleccionada")
        
        # Seleccionar formato BibTeX
        print("Seleccionando formato BibTeX...")
        bibtex_input = playwright_page.locator("//label[.//span[normalize-space()='BibTeX']]/input")
        playwright_page.evaluate("""
            (element) => {
                element.checked = true;
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """, bibtex_input.element_handle())
        time.sleep(2)
        print("✓ Formato BibTeX seleccionado")
        
        # Seleccionar "Citation and Abstract"
        print("Seleccionando formato de citaciones...")
        citation_input = playwright_page.locator("//label[.//span[normalize-space()='Citation and Abstract']]/input")
        playwright_page.evaluate("""
            (element) => {
                element.checked = true;
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """, citation_input.element_handle())
        time.sleep(4)
        print("✓ Citation and Abstract seleccionado")
        
        # Hacer clic en Download
        print("Clickeando 'Download'...")
        
        # Esperar la descarga
        with playwright_page.expect_download(timeout=30000) as download_info:
            download_button = playwright_page.locator("button.stats-SearchResults_Citation_Download.xpl-btn-primary")
            download_button.wait_for(state="visible", timeout=10000)
            download_button.click()
        
        # Obtener el objeto de descarga
        download = download_info.value
        
        # Guardar con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"ieee_page{page}_{timestamp}.bib"
        final_path = output_dir / final_filename
        
        download.save_as(final_path)
        print(f"✓ Descarga realizada: {final_filename}")
        
        # Contar entradas en el archivo
        with open(final_path, 'r', encoding='utf-8') as f:
            content = f.read()
            entries = content.count('@')
            print(f"✓ Entradas en archivo: {entries}")
        
        time.sleep(2)
        return entries
        
    except Exception as e:
        print(f"✗ Error en el scraping de página {page}: {e}")
        playwright_page.screenshot(path=f"error_page{page}.png")
        print(f"✓ Screenshot guardado: error_page{page}.png")
        return 0


def main():
    """
    Función principal para ejecutar el scraper
    """
    # Configurar directorios
    download_dir = Path("downloads").resolve()
    output_dir = Path("data/raw/IEEE")
    download_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Solicitar entrada del usuario
    try:
        start = int(input("Página de Inicio (e.g. 1): "))
        count = int(input("¿Cuántas páginas para el scrape?: "))
    except ValueError:
        print("✗ Entrada inválida")
        return
    
    print(f"\n{'='*60}")
    print(f"IEEE XPLORE SCRAPER CON PLAYWRIGHT")
    print(f"Páginas: {start} a {start + count - 1}")
    print(f"{'='*60}\n")
    
    # Iniciar Playwright
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.firefox.launch(
            headless=False,  # Cambiar a True para modo sin interfaz
            downloads_path=str(download_dir)
        )
        
        # Crear contexto
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0'
        )
        
        # Crear página
        page = context.new_page()
        page.set_default_timeout(30000)
        
        total_entries = 0
        successful_pages = 0
        
        # Recorrer las páginas
        for i in range(start, start + count):
            print(f"\n{'='*60}")
            print(f">>> Scraping página {i}/{start + count - 1}")
            print(f"{'='*60}")
            
            entries = scrape_ieee_bibtex(i, page, download_dir, output_dir)
            
            if entries > 0:
                total_entries += entries
                successful_pages += 1
            
            print(f"\nProgreso: {successful_pages}/{i - start + 1} páginas exitosas")
            print(f"Total de entradas descargadas: {total_entries}")
            
            # Esperar entre páginas
            if i < start + count - 1:
                print("\nEsperando antes de la siguiente página...")
                time.sleep(3)
        
        # Resumen final
        print(f"\n{'='*60}")
        print(f"RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"Páginas procesadas: {count}")
        print(f"Páginas exitosas: {successful_pages}")
        print(f"Total de entradas: {total_entries}")
        print(f"Archivos guardados en: {output_dir}")
        print(f"{'='*60}\n")
        
        # Cerrar navegador
        print("Cerrando navegador...")
        browser.close()
    
    # Preguntar si combinar archivos
    response = input("¿Deseas combinar todos los archivos .bib en uno solo? (s/n): ").strip().lower()
    if response == 's':
        combine_bib_files(output_dir)


def combine_bib_files(output_dir: Path):
    """
    Combina todos los archivos BibTeX en uno solo
    """
    bib_files = sorted(output_dir.glob("ieee_page*.bib"))
    
    if not bib_files:
        print("✗ No se encontraron archivos para combinar")
        return
    
    print(f"\n{'='*60}")
    print(f"Combinando {len(bib_files)} archivos...")
    print(f"{'='*60}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_file = output_dir / f"ieee_combined_{timestamp}.bib"
    
    combined_content = ""
    total_entries = 0
    
    for bib_file in bib_files:
        print(f"  Añadiendo: {bib_file.name}")
        with open(bib_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_content += content + "\n\n"
            total_entries += content.count('@')
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    print(f"\n✓ Archivo combinado creado: {combined_file}")
    print(f"✓ Total de entradas: {total_entries}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()