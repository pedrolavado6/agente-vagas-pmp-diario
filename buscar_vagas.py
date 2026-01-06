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

import os

status = []

if len(df) == 0:
    status.append("⚠️ Nenhuma vaga encontrada hoje.")
else:
    status.append(f"✅ {len(df)} vagas encontradas.")

status_text = "\n".join(status)

with open("STATUS.txt", "w", encoding="utf-8") as f:
    f.write(status_text)

print(status_text)

from datetime import datetime

status_lines = []
status_lines.append(f"Data: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

if len(df) == 0:
    status_lines.append("⚠️ Nenhuma vaga encontrada hoje.")
else:
    status_lines.append(f"✅ {len(df)} vagas encontradas.")

import requests
import os

TOKEN = os.getenv("8444083307:AAGuVa0LorqzVoX2IXPa75brXrN0DKrLGWU")
CHAT_ID = os.getenv("995833336")

if TOKEN and CHAT_ID:
    message = "Teste enviado com sucesso ✅"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    r = requests.post(url, data=payload)
    print(r.json())

with open("STATUS.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(status_lines))

print("\n".join(status_lines))
