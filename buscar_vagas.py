import feedparser
import pandas as pd
from datetime import datetime
import requests
import os

print("DEBUG: Script iniciado")

# -----------------------
# CONFIGURAÇÃO
# -----------------------
feeds = [
    "https://www.indeed.com/rss?q=project+manager+pmp+remote",
    "https://remoteok.com/remote-pm-jobs.rss",
    "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"
]

keywords = ["pmp", "project manager", "program manager", "pmo", "senior project"]

repo_dir = os.getenv("GITHUB_WORKSPACE", ".")
data_str = datetime.utcnow().strftime("%Y-%m-%d")

# -----------------------
# BUSCAR VAGAS
# -----------------------
vagas = []
for url in feeds:
    feed = feedparser.parse(url)
    for e in feed.entries:
        vagas.append({
            "Data": data_str,
            "Título": e.get("title", "Sem título"),
            "Empresa": e.get("author", "Não especificado"),
            "Link": e.get("link", "")
        })

df = pd.DataFrame(vagas)

if not df.empty:
    df = df[df["Título"].str.lower().str.contains("|".join(keywords), na=False)]
    df = df.drop_duplicates(subset=["Link"])

# -----------------------
# GUARDAR FICHEIROS
# -----------------------
csv_path = os.path.join(repo_dir, f"vagas_{data_str}.csv")
html_path = os.path.join(repo_dir, f"vagas_{data_str}.html")
status_path = os.path.join(repo_dir, "STATUS.txt")

df.to_csv(csv_path, index=False)
df.to_html(html_path, index=False)

# -----------------------
# STATUS
# -----------------------
if df.empty:
    status_text = f"Data: {data_str} UTC\n⚠️ Nenhuma vaga encontrada."
else:
    status_text = f"Data: {data_str} UTC\n✅ {len(df)} vagas encontradas."

with open(status_path, "w", encoding="utf-8") as f:
    f.write(status_text)

print(status_text)

# -----------------------
# TELEGRAM (TEXTO SIMPLES)
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TOKEN and CHAT_ID:
    try:
        resumo = status_text + "\n\nTop vagas:\n"

        for _, row in df.head(5).iterrows():
            resumo += f"- {row['Título']}\n{row['Link']}\n\n"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": resumo
        }

        r = requests.post(url, data=payload)
        print("Telegram:", r.json())

    except Exception as e:
        print("Erro Telegram:", e)
else:
    print("Secrets do Telegram não disponíveis")
