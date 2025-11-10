from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px


def generate_wordcloud(df: pd.DataFrame, out_path: Path, max_words: int = 200):
    text = ' '.join(df['text_for_wordcloud'].dropna().tolist())
    if not text.strip():
        print('No hay texto para wordcloud')
        return None
    wc = WordCloud(width=1200, height=600, background_color='white', max_words=max_words)
    wc.generate(text)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wc.to_file(str(out_path))
    print(f'Wordcloud guardada en {out_path}')
    return out_path


def generate_timeline(df: pd.DataFrame, out_path: Path, top_n_journals: int = 8):
    df_year = df.dropna(subset=['year']).copy()
    df_year['year'] = df_year['year'].astype(int)
    # publicaciones por año
    yearly = df_year.groupby('year').size().reset_index(name='count')
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=yearly, x='year', y='count', marker='o')
    plt.title('Publicaciones por año')
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    year_img = out_path.with_name(out_path.stem + '_year.png')
    plt.savefig(year_img)
    plt.close()
    print(f'Timeline (año) guardado en {year_img}')

    # por revista: top N
    top_j = df_year['journal'].value_counts().nlargest(top_n_journals).index.tolist()
    df_top = df_year[df_year['journal'].isin(top_j)]
    pivot = df_top.groupby(['year', 'journal']).size().reset_index(name='count')
    pivot = pivot.pivot(index='year', columns='journal', values='count').fillna(0)
    pivot.plot(kind='bar', stacked=True, figsize=(12, 5))
    plt.title(f'Publicaciones por año (Top {top_n_journals} revistas)')
    plt.tight_layout()
    journal_img = out_path.with_name(out_path.stem + '_journal.png')
    plt.savefig(journal_img)
    plt.close()
    print(f'Timeline (revistas) guardado en {journal_img}')

    return [year_img, journal_img]


def generate_map(df: pd.DataFrame, out_path: Path, location_field: str = 'country', title: str = 'Mapa de producción por país'):
    
    grouped = df.groupby(location_field).size().reset_index(name='count')
    grouped = grouped[grouped[location_field].notna() & (grouped[location_field] != '')]
    if grouped.empty:
        print('No hay países conocidos para generar el mapa')
        return None

    fig = px.choropleth(grouped, locations=location_field, locationmode='country names', color='count', hover_name=location_field, color_continuous_scale='Viridis')
    fig.update_layout(title=title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.write_image(str(out_path))
    print(f'Mapa guardado en {out_path}')
    return out_path
