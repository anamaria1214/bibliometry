#!/usr/bin/env python3
"""
Hierarchical clustering and dendrogram generation for corpus of abstracts.

Usage examples:
  python src/requerimiento4/hierarchical_clustering.py --method tfidf --max-docs 200
  python src/requerimiento4/hierarchical_clustering.py --method embeddings --max-docs 100 --linkages single complete ward

This script reads `data/processed/unified_references.bib`, extracts abstracts (and titles for labels),
computes document vectors (TF-IDF or SentenceTransformers embeddings), computes pairwise distances,
applies hierarchical clustering (single, complete, ward) and saves dendrogram PNGs and stats.
"""

import argparse
from pathlib import Path
import re
import sys
import math
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet

try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except Exception:
    _HAS_ST = False

# Calcular la ruta raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def read_bib_file_extract_abstracts(bib_path: Path):
    text = bib_path.read_text(encoding="utf-8", errors="ignore")
    raw_entries = re.findall(r'@[\w]+\s*{[^@]*}', text, flags=re.DOTALL | re.IGNORECASE)
    results = []
    for idx, entry in enumerate(raw_entries, start=1):
        # key
        mkey = re.match(r'@[\w]+\s*{\s*([^,]+),', entry)
        key = mkey.group(1).strip() if mkey else f"entry_{idx}"
        # title
        mtitle = re.search(r'title\s*=\s*[{"](.+?)[}"]\s*,', entry, flags=re.IGNORECASE | re.DOTALL)
        title = mtitle.group(1).strip().replace('\n', ' ') if mtitle else key
        # abstract
        mabs = re.search(r'abstract\s*=\s*[{"](.+?)[}"]\s*,', entry, flags=re.IGNORECASE | re.DOTALL)
        abstract = ''
        if mabs:
            abstract = mabs.group(1).strip().replace('\n', ' ')
        else:
            # fallback without trailing comma
            mabs2 = re.search(r'abstract\s*=\s*[{"](.+?)[}"]\s*$', entry, flags=re.IGNORECASE | re.DOTALL)
            if mabs2:
                abstract = mabs2.group(1).strip().replace('\n', ' ')
        results.append({'key': key, 'title': title, 'abstract': abstract})
    return results


def compute_tfidf_vectors(docs, max_features=8000, ngram_range=(1,2)):
    vec = TfidfVectorizer(ngram_range=ngram_range, stop_words='english', max_features=max_features)
    X = vec.fit_transform(docs)
    return X.toarray(), vec


def compute_embedding_vectors(docs, model_name='all-MiniLM-L6-v2', batch_size=64):
    if not _HAS_ST:
        raise RuntimeError('sentence-transformers not installed; cannot compute embeddings')
    model = SentenceTransformer(model_name)
    emb = model.encode(docs, batch_size=batch_size, show_progress_bar=True)
    return np.array(emb), model


def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def make_dendrogram(Z, labels, out_path: Path, title: str, figsize=(12, 6), truncate_mode=None):
    plt.figure(figsize=figsize)
    dendrogram(Z, labels=labels, leaf_rotation=90, leaf_font_size=8, truncate_mode=truncate_mode)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--bib', type=str, default=str(PROJECT_ROOT / 'data/processed/unified_references.bib'))
    parser.add_argument('--method', choices=['tfidf', 'embeddings'], default='tfidf')
    parser.add_argument('--max-docs', type=int, default=200, help='Max number of documents to cluster (keeps plots readable)')
    parser.add_argument('--linkages', nargs='+', default=['single', 'complete', 'ward'], help='Linkage methods to compute')
    parser.add_argument('--output-dir', type=str, default=str(PROJECT_ROOT / 'data/analysis/dendrograms'))
    parser.add_argument('--model-name', type=str, default='all-MiniLM-L6-v2', help='SentenceTransformers model name')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args(argv)

    bib_path = Path(args.bib)
    if not bib_path.exists():
        print(f"ERROR: {bib_path} not found")
        sys.exit(1)

    ensure_output_dir(Path(args.output_dir))

    print('Reading .bib and extracting abstracts...')
    entries = read_bib_file_extract_abstracts(bib_path)
    # filter those with non-empty abstracts
    entries = [e for e in entries if e['abstract'].strip()]
    if not entries:
        print('No abstracts found in the .bib file. Aborting.')
        sys.exit(0)

    # limit docs
    if args.max_docs and len(entries) > args.max_docs:
        entries = entries[:args.max_docs]

    keys = [e['key'] for e in entries]
    titles = [e['title'] for e in entries]
    docs = [e['abstract'] for e in entries]

    print(f'Documents to process: {len(docs)}')

    # compute vectors
    if args.method == 'tfidf':
        print('Computing TF-IDF vectors...')
        X, vec = compute_tfidf_vectors(docs)
        # for cosine distances
        sim = cosine_similarity(X)
        # distance matrix = 1 - cosine
        dist_matrix = 1.0 - sim
    else:
        print(f'Computing embeddings with model {args.model_name}...')
        X, model = compute_embedding_vectors(docs, model_name=args.model_name)
        sim = cosine_similarity(X)
        dist_matrix = 1.0 - sim

    # condensed distance required for linkage
    condensed = pdist(X if 'ward' in args.linkages else dist_matrix, metric='euclidean' if 'ward' in args.linkages else 'euclidean')
    # Note: the above choice ensures compatible distances for ward; for single/complete we will compute properly below per linkage

    results = []
    for link in args.linkages:
        print(f'Processing linkage: {link}')
        try:
            if link == 'ward':
                # Ward requires Euclidean distances on feature vectors
                condensed_link = pdist(X, metric='euclidean')
            else:
                # use cosine distance for single/complete
                condensed_link = pdist(sim, metric='cosine') if False else pdist(X, metric='cosine')
                # Using pdist on X with 'cosine' will compute 1 - cosine similarity

            Z = linkage(condensed_link, method=link)
            # compute cophenetic correlation
            coph_corr, coph_dists = cophenet(Z, condensed_link)
            print(f'  Cophenetic correlation ({link}): {coph_corr:.4f}')

            # prepare labels (shorten titles)
            short_labels = [t if len(t) <= 60 else t[:57] + '...' for t in titles]

            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            out_png = Path(args.output_dir) / f'dendrogram_{args.method}_{link}_{ts}.png'
            make_dendrogram(Z, short_labels, out_png, title=f'Dendrogram ({args.method}, {link})')
            print(f'  Saved dendrogram: {out_png}')

            results.append({'linkage': link, 'cophenetic': float(coph_corr), 'n_docs': len(docs), 'output': str(out_png)})

        except Exception as e:
            print(f'  ✗ Error processing linkage {link}: {e}')
            continue

    # Save summary
    summary_df = pd.DataFrame(results)
    summary_file = Path(args.output_dir) / f'dendrogram_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    summary_df.to_csv(summary_file, index=False)
    print(f'Summary saved to: {summary_file}')


if __name__ == '__main__':
    main()
