import feedparser
import pandas as pd
from datetime import datetime
import requests
import os

# -----------------------
# CONFIGURAÇÃO DE FEEDS
# -----------------------
feeds = [
    "https://www.indeed.com/rss?q=project+manager+pmp+remote",
    "https://remoteok.com/remote-pm-jobs.rss",
    "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"
]

# Palavras-chave para filtrar vagas
keywords = ["pmp", "project manager", "program manager", "pmo", "senior project"]

# -----------------------
# BUSCA DAS VAGAS
# -----------------------
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

# Converter para DataFrame
df = pd.DataFrame(vagas)

# Filtrar por palavras-chave
df = df[df["Resumo"].str.lower().str.contains("|".join(keywords), na=False)]

# Remover duplicados
df = df.drop_duplicates(subset=["Link"])

# -----------------------
# SALVAR ARQUIVOS
# -----------------------
data_str = datetime.utcnow().strftime("%Y-%m-%d")
csv_filename = f"vagas_{data_str}.csv"
html_filename = f"vagas_{data_str}.html"

df.to_csv(csv_filename, index=False)
df.to_html(html_filename, index=False)

# -----------------------
# CRIAR STATUS.TXT
# -----------------------
status_lines = []
status_lines.append(f"Data: {data_str} UTC")
if len(df) == 0:
    status_lines.append("⚠️ Nenhuma vaga encontrada hoje.")
else:
    status_lines.append(f"✅ {len(df)} vagas encontradas.")

with open("STATUS.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(status_lines))

print("\n".join(status_lines))

# -----------------------
# ENVIO PARA TELEGRAM
# -----------------------
TOKEN = os.getenv("8444083307:AAGuVa0LorqzVoX2IXPa75brXrN0DKrLGWU")
CHAT_ID = os.getenv("5096956870")

if TOKEN and CHAT_ID:
    try:
        # Ler HTML completo
        with open(html_filename, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Limitar a 3500 caracteres (Telegram tem limite)
        max_len = 3500
        message = "\n".join(status_lines) + "\n\n" + html_content[:max_len]

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        response = requests.post(url, data=payload)
        result = response.json()
        print("Telegram:", result)

        if not result.get("ok", False):
            print("⚠️ Falha ao enviar mensagem para Telegram:", result)
    except Exception as e:
        print("⚠️ Erro ao enviar Telegram:", e)
else:
    print("⚠️ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos. Mensagem não enviada.")
