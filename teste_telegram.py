import os
import requests

TOKEN = os.getenv("8444083307:AAGuVa0LorqzVoX2IXPa75brXrN0DKrLGWU")
CHAT_ID = os.getenv("5096956870")

message = "✅ Teste de envio do bot, funciona! By PL"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message}

r = requests.post(url, data=payload)
print(r.json())
