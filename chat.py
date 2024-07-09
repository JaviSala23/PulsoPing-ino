import requests

TOKEN = '7157402657:AAHIiCK42UKAslXGH0SU0HDpyBwEjjo0xo4'
URL = f'https://api.telegram.org/bot{TOKEN}/getUpdates'

response = requests.get(URL)
data = response.json()

# Imprimir el JSON completo para inspeccionarlo
print(data)

# Extraer chat_id del primer mensaje recibido
if 'result' in data and len(data['result']) > 0:
    chat_id = data['result'][0]['message']['chat']['id']
    print(f"Tu chat_id es: {chat_id}")
else:
    print("No se encontraron mensajes. Envía un mensaje a tu bot y vuelve a intentarlo.")