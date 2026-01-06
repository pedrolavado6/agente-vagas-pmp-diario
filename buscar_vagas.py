import feedparser
import pandas as pd
from datetime import datetime
import requests
import os

# --- Feeds ---
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
            "Data": datetime.utcnow().strftime("%Y-%m-%d"),
            "Titulo": e.get("title",""),
            "Empresa": e.get("author","Não especificado"),
            "Link": e.get("link",""),
            "Resumo": e.get("summary","")
        })

df = pd.DataFrame(vagas)

# --- Filtrar palavras-chave ---
keywords = ["pmp","project manager","program manager","pmo","senior project"]
df = df[df["Resumo"].str.lower().str.contains("|".join(keywords), na=False)]
df = df.drop_duplicates(subset=["Link"])

# --- Guardar ficheiros ---
data_str = datetime.utcnow().strftime("%Y-%m-%d")
csv_filename = f"vagas_{data_str}.csv"
html_filename = f"vagas_{data_str}.html"

df.to_csv(csv_filename,index=False)
df.to_html(html_filename,index=False)

# --- Criar STATUS ---
status_text = f"📊 Vagas PMP – {data_str}\nTotal vagas: {len(df)}"
with open("STATUS.txt","w",encoding="utf-8") as f:
    f.write(status_text)

# --- Enviar para Telegram ---
token = os.getenv("8444083307:AAGuVa0LorqzVoX2IXPa75brXrN0DKrLGWU")
chat_id = os.getenv("5096956870")

if token and chat_id:
    # Ler HTML
    with open(html_filename,"r",encoding="utf-8") as f:
        html_content = f.read()

    # Mensagem com limite de caracteres
    max_len = 3500
    message = status_text + "\n\n" + html_content[:max_len]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    requests.post(url, data=payload)

print("Execução completa. Status enviado ao Telegram.")
