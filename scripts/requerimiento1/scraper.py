from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path
import time
import re

def download_arxiv(search_query: str = "generative artificial intelligence", max_results: int = 1000):
    """
    Descarga artículos de arXiv (muy confiable y sin restricciones)
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        all_entries = []
        results_per_page = 200
        start = 0
        
        print(f"{'='*60}")
        print(f"Descargando desde arXiv: {search_query}")
        print(f"{'='*60}\n")
        
        try:
            while len(all_entries) < max_results:
                url = f"https://arxiv.org/search/?query={search_query.replace(' ', '+')}&searchtype=all&abstracts=show&order=-announced_date_first&size={results_per_page}&start={start}"
                
                print(f"Página {start//results_per_page + 1} (Start: {start})...")
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(2)
                
                # Extraer IDs de arXiv
                articles = page.locator("li.arxiv-result").all()
                print(f"  ✓ Encontrados {len(articles)} artículos en esta página")
                
                if len(articles) == 0:
                    print("  ✗ No hay más resultados")
                    break
                
                for article in articles:
                    try:
                        # Extraer ID de arXiv
                        link = article.locator("p.list-title a").first.get_attribute("href")
                        arxiv_id = link.split("/abs/")[-1]
                        all_entries.append(arxiv_id)
                        
                        if len(all_entries) >= max_results:
                            break
                    except Exception as e:
                        continue
                
                print(f"  Total acumulado: {len(all_entries)}")
                
                if len(all_entries) >= max_results:
                    break
                
                start += results_per_page
                time.sleep(2)
            
            # Ahora descargar BibTeX para todos los IDs
            print(f"\n{'='*60}")
            print(f"Generando archivo BibTeX para {len(all_entries)} artículos...")
            print(f"{'='*60}\n")
            
            # arXiv permite descargar BibTeX directamente
            bibtex_content = ""
            batch_size = 50
            
            for i in range(0, len(all_entries), batch_size):
                batch = all_entries[i:i+batch_size]
                print(f"Procesando lote {i//batch_size + 1}/{(len(all_entries)-1)//batch_size + 1}...")
                
                for arxiv_id in batch:
                    # Ir a la página de exportación
                    export_url = f"https://arxiv.org/bibtex/{arxiv_id}"
                    page.goto(export_url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(0.5)
                    
                    # Extraer el BibTeX
                    try:
                        pre_content = page.locator("pre").first.inner_text()
                        bibtex_content += pre_content + "\n\n"
                    except:
                        print(f"  ✗ Error con {arxiv_id}")
                
                time.sleep(1)
            
            # Guardar archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"arxiv_{timestamp}.bib"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(bibtex_content)
            
            entries_count = bibtex_content.count('@')
            print(f"\n✓ Archivo guardado: {output_file}")
            print(f"✓ Total de entradas: {entries_count}")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
        finally:
            browser.close()


def download_semantic_scholar(search_query: str = "generative artificial intelligence", max_results: int = 1000):
    """
    Descarga artículos de Semantic Scholar (API pública disponible)
    """
    import requests
    
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{'='*60}")
    print(f"Descargando desde Semantic Scholar: {search_query}")
    print(f"{'='*60}\n")
    
    all_papers = []
    offset = 0
    limit = 100
    
    try:
        while len(all_papers) < max_results:
            print(f"Solicitando papers (offset: {offset})...")
            
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': search_query,
                'offset': offset,
                'limit': limit,
                'fields': 'title,authors,year,venue,citationCount,abstract,externalIds'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f"✗ Error en API: {response.status_code}")
                break
            
            data = response.json()
            papers = data.get('data', [])
            
            if not papers:
                print("✗ No hay más resultados")
                break
            
            all_papers.extend(papers)
            print(f"  ✓ Obtenidos {len(papers)} papers (Total: {len(all_papers)})")
            
            offset += limit
            time.sleep(1)  # Respetar rate limit
            
            if len(all_papers) >= max_results:
                all_papers = all_papers[:max_results]
                break
        
        # Convertir a BibTeX
        print(f"\n{'='*60}")
        print("Generando archivo BibTeX...")
        print(f"{'='*60}\n")
        
        bibtex_content = ""
        
        for i, paper in enumerate(all_papers):
            try:
                # Generar citation key
                first_author = paper.get('authors', [{}])[0].get('name', 'Unknown').split()[-1]
                year = paper.get('year', 'n.d.')
                citation_key = f"{first_author}{year}_{i}"
                
                # Crear entrada BibTeX
                title = paper.get('title', 'Untitled').replace('{', '').replace('}', '')
                authors = ' and '.join([a.get('name', '') for a in paper.get('authors', [])])
                venue = paper.get('venue', 'Unknown')
                abstract = paper.get('abstract', '')
                
                # Determinar tipo (article o inproceedings)
                entry_type = 'inproceedings' if 'conference' in venue.lower() or 'proceedings' in venue.lower() else 'article'
                
                bibtex_entry = f"@{entry_type}{{{citation_key},\n"
                bibtex_entry += f"  title = {{{title}}},\n"
                bibtex_entry += f"  author = {{{authors}}},\n"
                bibtex_entry += f"  year = {{{year}}},\n"
                
                if entry_type == 'article':
                    bibtex_entry += f"  journal = {{{venue}}},\n"
                else:
                    bibtex_entry += f"  booktitle = {{{venue}}},\n"
                
                if abstract:
                    bibtex_entry += f"  abstract = {{{abstract}}},\n"
                
                # Agregar DOI si existe
                external_ids = paper.get('externalIds', {})
                if 'DOI' in external_ids:
                    bibtex_entry += f"  doi = {{{external_ids['DOI']}}},\n"
                
                bibtex_entry += "}\n\n"
                bibtex_content += bibtex_entry
                
            except Exception as e:
                print(f"  ✗ Error procesando paper {i}: {e}")
                continue
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"semantic_scholar_{timestamp}.bib"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        
        entries_count = bibtex_content.count('@')
        print(f"Archivo guardado: {output_file}")
        print(f"Total de entradas: {entries_count}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


def download_pubmed(search_query: str = "generative artificial intelligence", max_results: int = 1000):
    """
    Descarga artículos de PubMed (biomedicina, pero tiene muchos artículos de IA también)
    """
    from urllib.parse import quote
    import requests
    import xml.etree.ElementTree as ET
    
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{'='*60}")
    print(f"Descargando desde PubMed: {search_query}")
    print(f"{'='*60}\n")
    
    try:
        # Paso 1: Buscar IDs
        print("Buscando artículos...")
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': search_query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        response = requests.get(search_url, params=params)
        data = response.json()
        
        id_list = data.get('esearchresult', {}).get('idlist', [])
        print(f"✓ Encontrados {len(id_list)} artículos\n")
        
        if not id_list:
            print("✗ No se encontraron resultados")
            return
        
        # Paso 2: Obtener detalles en lotes
        print("Descargando metadatos...")
        bibtex_content = ""
        batch_size = 200
        
        for i in range(0, len(id_list), batch_size):
            batch = id_list[i:i+batch_size]
            print(f"  Lote {i//batch_size + 1}/{(len(id_list)-1)//batch_size + 1}...")
            
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(batch),
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params)
            root = ET.fromstring(response.content)
            
            # Parsear XML y convertir a BibTeX
            for article in root.findall('.//PubmedArticle'):
                try:
                    pmid = article.find('.//PMID').text
                    
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else 'Untitled'
                    
                    # Autores
                    authors = []
                    for author in article.findall('.//Author'):
                        lastname = author.find('LastName')
                        forename = author.find('ForeName')
                        if lastname is not None:
                            name = lastname.text
                            if forename is not None:
                                name = f"{forename.text} {name}"
                            authors.append(name)
                    
                    # Año
                    year_elem = article.find('.//PubDate/Year')
                    year = year_elem.text if year_elem is not None else 'n.d.'
                    
                    # Journal
                    journal_elem = article.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else 'Unknown'
                    
                    # Abstract
                    abstract_elem = article.find('.//Abstract/AbstractText')
                    abstract = abstract_elem.text if abstract_elem is not None else ''
                    
                    # DOI
                    doi = None
                    for article_id in article.findall('.//ArticleId'):
                        if article_id.get('IdType') == 'doi':
                            doi = article_id.text
                            break
                    
                    # Crear entrada BibTeX
                    citation_key = f"PMID{pmid}"
                    
                    bibtex_entry = f"@article{{{citation_key},\n"
                    bibtex_entry += f"  title = {{{title}}},\n"
                    bibtex_entry += f"  author = {{{' and '.join(authors)}}},\n"
                    bibtex_entry += f"  journal = {{{journal}}},\n"
                    bibtex_entry += f"  year = {{{year}}},\n"
                    bibtex_entry += f"  pmid = {{{pmid}}},\n"
                    
                    if doi:
                        bibtex_entry += f"  doi = {{{doi}}},\n"
                    if abstract:
                        bibtex_entry += f"  abstract = {{{abstract}}},\n"
                    
                    bibtex_entry += "}\n\n"
                    bibtex_content += bibtex_entry
                    
                except Exception as e:
                    continue
            
            time.sleep(0.5)  # Respetar rate limit
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"pubmed_{timestamp}.bib"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        
        entries_count = bibtex_content.count('@')
        print(f"\n✓ Archivo guardado: {output_file}")
        print(f"✓ Total de entradas: {entries_count}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    print("="*60)
    print("SCRAPER MULTI-BASE DE DATOS")
    print("="*60)
    print("\nBases de datos disponibles:")
    print("1. arXiv (Física, CS, Matemáticas - MUY CONFIABLE)")
    print("2. Semantic Scholar (Multidisciplinario - API PÚBLICA)")
    print("3. PubMed (Biomedicina/Salud - API PÚBLICA)")
    print("\nRecomendación: Semantic Scholar o arXiv")
    
    choice = input("\nElige base de datos (1, 2 o 3): ").strip()
    search_query = input("Término de búsqueda [generative artificial intelligence]: ").strip()
    if not search_query:
        search_query = "generative artificial intelligence"
    
    max_results = input("Número máximo de resultados [1000]: ").strip()
    max_results = int(max_results) if max_results else 1000
    
    print()
    
    if choice == "1":
        download_arxiv(search_query, max_results)
    elif choice == "2":
        download_semantic_scholar(search_query, max_results)
    elif choice == "3":
        download_pubmed(search_query, max_results)
    else:
        print("Opción inválida")
    
    print("\n" + "="*60)
    print("✓ PROCESO COMPLETADO")
    print("="*60) 