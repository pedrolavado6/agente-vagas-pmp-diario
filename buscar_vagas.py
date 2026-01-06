import feedparser
import pandas as pd
from datetime import datetime

feeds = [
    "https://www.indeed.com/rss?q=project+manager+pmp+remote",
    "https://remoteok.com/remote-pm-jobs.rss",
    "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"
]

vagas = []

for url in feeds:
    feed = feedparser.parse(url)
    for e in feed.entries:
        vagas.append({
            "Data_coleta": datetime.utcnow().strftime("%Y-%m-%d"),
            "Titulo": e.get("title", ""),
            "Empresa": e.get("author", "Não especificado"),
            "Link": e.get("link", ""),
            "Resumo": e.get("summary", "")
        })

df = pd.DataFrame(vagas)

palavras_chave = [
    "pmp",
    "project manager",
    "program manager",
    "pmo",
    "senior project"
]

df = df[df["Resumo"].str.lower().str.contains("|".join(palavras_chave), na=False)]
df = df.drop_duplicates(subset=["Link"])

data = datetime.utcnow().strftime("%Y-%m-%d")

df.to_csv(f"vagas_{data}.csv", index=False)
df.to_html(f"vagas_{data}.html", index=False)

print("Execução concluída com sucesso.")
print(f"Registos encontrados: {len(df)}")
