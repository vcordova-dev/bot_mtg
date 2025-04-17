import requests

# Substitua pelos seus valores
client_id = 'a1b836bc-007e-4f87-a89e-cb7447ade43c'
client_secret = 'iM.8Q~7aV85EMCWVl2HLQFyHNYAwk9zXjbbijaD8'
tenant_id = '5abb7ec4-ed77-4480-af66-bbf3f1eea63f'
webhook_url = 'https://prod-05.brazilsouth.logic.azure.com:443/workflows/06c4cf82573c43eabda35cc6b274a2e6/triggers/manual/paths/invoke?api-version=2016-06-01'

# 1. Obter o token
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'resource': 'https://service.flow.microsoft.com/'  # ou o recurso necessário pelo Power Automate
}

token_response = requests.post(token_url, data=token_data)
access_token = token_response.json().get('access_token')

# 2. Enviar a requisição autenticada
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

payload = {
    "numbers": [10, 20, 30],
    "source": "Python com OAuth"
}

response = requests.post(webhook_url, headers=headers, json=payload)

print(response.status_code, response.text)
