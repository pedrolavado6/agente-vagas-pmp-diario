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
    "https://www.indeed.com/rss?q=project+manager+remote",
    "https://www.indeed.co.uk/rss?q=project+manager+remote",
    "https://www.indeed.ie/rss?q=project+manager+remote",
    "https://remoteok.com/remote-pm-jobs.rss",
    "https://remotive.com/remote-jobs/project-management/rss",
    "https://www.weworkremotely.com/categories/remote-management-and-finance-jobs.rss",
    "https://www.workingnomads.com/jobs/rss",
    "https://jobicy.com/rss"
]

repo_dir = os.getenv("GITHUB_WORKSPACE", ".")
data_str = datetime.utcnow().strftime("%Y-%m-%d")

# -----------------------
# FUNÇÕES AUXILIARES
# -----------------------
def classificar_pmp(texto):
    return "PMP explícito" if "pmp" in texto.lower() else "PMP desejável"

def classificar_salario(texto):
    t = texto.lower()
    if any(x in t for x in ["director", "principal", "head", "vp"]):
        return "€€€€"
    if any(x in t for x in ["senior", "lead", "staff"]):
        return "€€€"
    if any(x in t for x in ["manager"]):
        return "€€"
    return "€"

# -----------------------
# BUSCAR VAGAS
# -----------------------
vagas = []

for url in feeds:
    feed = feedparser.parse(url)
    for e in feed.entries:
        titulo = e.get("title", "")
        resumo = e.get("summary", "")
        texto = f"{titulo} {resumo}"

        if any(k in texto.lower() for k in ["project", "program", "pmo"]):
            vagas.append({
                "Data": data_str,
                "Título": titulo,
                "Empresa": e.get("author", "Não especificado"),
                "Link": e.get("link", ""),
                "Classificação PMP": classificar_pmp(texto),
                "Ranking Salarial": classificar_salario(texto)
            })

df = pd.DataFrame(vagas).drop_duplicates(subset=["Link"])

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
total = len(df)
pmp_exp = len(df[df["Classificação PMP"] == "PMP explícito"])
pmp_des = len(df[df["Classificação PMP"] == "PMP desejável"])

status_text = (
    f"📅 {data_str} UTC\n"
    f"📊 Total de vagas: {total}\n"
    f"🎓 PMP explícito: {pmp_exp}\n"
    f"🧩 PMP desejável: {pmp_des}"
)

with open(status_path, "w", encoding="utf-8") as f:
    f.write(status_text)

print(status_text)

# -----------------------
# TELEGRAM
# -----------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_texto(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def enviar_ficheiro(path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": CHAT_ID})

if TOKEN and CHAT_ID:
    try:
        # 1️⃣ Mensagem resumo
        resumo = status_text + "\n\nTop vagas:\n"
        for _, row in df.sort_values("Ranking Salarial", ascending=False).head(5).iterrows():
            resumo += f"- {row['Título']}\n{row['Link']}\n\n"

        if total == 0:
            resumo += "⚠️ Nenhuma vaga encontrada hoje."

        enviar_texto(resumo)

        # 2️⃣ Enviar CSV
        enviar_ficheiro(csv_path)

        # 3️⃣ Enviar HTML
        enviar_ficheiro(html_path)

        print("Telegram: mensagens e anexos enviados com sucesso")

    except Exception as e:
        print("Erro Telegram:", e)
else:
    print("Secrets do Telegram não disponíveis")
