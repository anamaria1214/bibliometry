"""Interfaz por consola

Se ejecuta con `python -m src.requerimiento5.cli_visualize`
o
`python src/requerimiento5/cli_visualize.py`.
"""

from pathlib import Path
import sys

# Calcular la ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Intentar importaciones de paquete; si fallan (ejecución directa), añadir la raíz del repo a sys.path
try:
    from src.requerimiento5.extract_metadata import parse_bib_file, save_metadata
    from src.requerimiento5.geolocation import resolve_country_by_doi
    from src.requerimiento5.plots import generate_wordcloud, generate_timeline, generate_map
except Exception:
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.requerimiento5.extract_metadata import parse_bib_file, save_metadata
    from src.requerimiento5.geolocation import resolve_country_by_doi
    from src.requerimiento5.plots import generate_wordcloud, generate_timeline, generate_map

from PIL import Image
import pandas as pd


def parse_and_resolve(bib_path: Path, use_crossref: bool = True):
    print('Parseando .bib...')
    df = parse_bib_file(bib_path)
    metadata_csv = PROJECT_ROOT / 'data/analysis/metadata.csv'
    save_metadata(df, metadata_csv)

    print('Resolviendo países por DOI (esto puede tardar si hay muchas entradas)')
    countries = []
    for doi in df['doi'].fillna('').tolist():
        country = None
        if use_crossref and doi:
            country = resolve_country_by_doi(doi)
        countries.append(country or '')
    df['country'] = countries
    save_metadata(df, metadata_csv)
    print('Resolución completada.')
    return df


def combine_images_to_pdf(img_paths, out_pdf: Path):
    pil_images = []
    for p in img_paths:
        try:
            im = Image.open(p).convert('RGB')
            pil_images.append(im)
        except Exception as e:
            print(f'No se pudo abrir imagen {p}: {e}')
    if pil_images:
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        first, rest = pil_images[0], pil_images[1:]
        first.save(out_pdf, save_all=True, append_images=rest)
        print(f'PDF generado en {out_pdf}')
    else:
        print('No hay imágenes válidas para generar PDF')


def interactive_menu():
    print('\n=== Visualizador de producción científica ===')
    default_bib = str(PROJECT_ROOT / 'data/processed/unified_references.bib')
    bib_path = input(f'Ruta al archivo .bib (por defecto {default_bib}): ').strip() or default_bib
    out_dir = input('Directorio de salida (por defecto reports): ').strip() or 'reports'
    use_crossref = input('Usar Crossref para resolver países? [Y/n]: ').strip().lower() != 'n'

    bib = Path(bib_path)
    out = Path(out_dir)

    df = None

    while True:
        print('\nSelecciona una opción:')
        print('1) Parsear .bib y resolver países (preparar metadata)')
        print('2) Generar nube de palabras')
        print('3) Generar línea temporal (año + revistas)')
        print('4) Generar mapa de calor por país')
        print('5) Generar PDF combinando las imágenes existentes')
        print('6) Ejecutar pipeline completo (1->2->3->4->5)')
        print('0) Salir')
        choice = input('Opción: ').strip()

        if choice == '1':
            df = parse_and_resolve(bib, use_crossref=use_crossref)

        elif choice == '2':
            if df is None:
                df = parse_and_resolve(bib, use_crossref=use_crossref)
            out_path = out / 'wordcloud.png'
            generate_wordcloud(df, out_path)

        elif choice == '3':
            if df is None:
                df = parse_and_resolve(bib, use_crossref=use_crossref)
            out_path = out / 'timeline'
            generate_timeline(df, out_path)

        elif choice == '4':
            if df is None:
                df = parse_and_resolve(bib, use_crossref=use_crossref)
            out_path = out / 'map.png'
            generate_map(df, out_path, location_field='country')

        elif choice == '5':
            # buscar imágenes en out dir
            imgs = list(out.glob('*.png')) + list(out.glob('timeline_*.png'))
            # add pattern matches for timeline images
            imgs = sorted(set(imgs))
            if not imgs:
                print('No se encontraron imágenes en', out)
            else:
                combine_images_to_pdf(imgs, out / 'visual_report.pdf')

        elif choice == '6':
            df = parse_and_resolve(bib, use_crossref=use_crossref)
            wc = generate_wordcloud(df, out / 'wordcloud.png')
            timgs = generate_timeline(df, out / 'timeline')
            m = generate_map(df, out / 'map.png', location_field='country')
            imgs = []
            if wc:
                imgs.append(wc)
            if timgs:
                imgs.extend(timgs)
            if m:
                imgs.append(m)
            combine_images_to_pdf(imgs, out / 'visual_report.pdf')

        elif choice == '0':
            print('Saliendo...')
            break

        else:
            print('Opción no válida')


if __name__ == '__main__':
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print('\nInterrumpido por el usuario')
        sys.exit(0)
