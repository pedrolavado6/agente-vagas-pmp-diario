import feedparser
import pandas as pd
from datetime import datetime
import requests
import os

# Feeds
feeds = [
    "https://www.indeed.com/rss?q=project+manager+pmp+remote",
    "https://remoteok.com/remote-pm-jobs.rss",
    "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"
]

keywords = ["pmp", "project manager", "program manager", "pmo", "senior project"]

# Buscar vagas
vagas = []
for url in feeds:
    feed = feedparser.parse(url)
    for e in feed.entries:
        vagas.append({
            "Data": datetime.utcnow().strftime("%Y-%m-%d"),
            "Titulo": e.get("title", "Sem título"),
            "Empresa": e.get("author", "Não especificado"),
            "Link": e.get("link", ""),
            "Resumo": e.get("summary", "")
        })

df = pd.DataFrame(vagas)
df = df[df["Resumo"].str.lower().str.contains("|".join(keywords), na=False)]
df = df.drop_duplicates(subset=["Link"])

# Salvar arquivos
data_str = datetime.utcnow().strftime("%Y-%m-%d")
csv_filename = f"vagas_{data_str}.csv"
html_filename = f"vagas_{data_str}.html"

df.to_csv(csv_filename, index=False)
df.to_html(html_filename, index=False)

# Criar status.txt
status_lines = [f"Data: {data_str} UTC"]
status_lines.append(f"✅ {len(df)} vagas encontradas." if len(df) > 0 else "⚠️ Nenhuma vaga encontrada hoje.")

with open("STATUS.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(status_lines))

print("\n".join(status_lines))

# Envio para Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TOKEN and CHAT_ID:
    try:
        with open(html_filename, "r", encoding="utf-8") as f:
            html_content = f.read()

        max_len = 3500
        message = "\n".join(status_lines) + "\n\n" + html_content[:max_len]

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}

        resp = requests.post(url, data=payload)
        print("Telegram:", resp.json())

    except Exception as e:
        print("⚠️ Erro ao enviar Telegram:", e)
else:
    print("⚠️ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos. Mensagem não enviada.")
