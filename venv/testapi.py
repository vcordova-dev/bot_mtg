import requests

def send_numbers_to_power_automate(numbers):
    POWER_AUTOMATE_WEBHOOK_URL = "https://prod-18.brazilsouth.logic.azure.com:443/workflows/1fd8ef1033e34cd3953513abb04ddfc2/triggers/manual/paths/invoke?api-version=2016-06-01"
    
    payload = {
        "numbers": numbers,
        "source": "Python Script"
    }
    
    try:
        response = requests.post(
            POWER_AUTOMATE_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("Números enviados com sucesso para o Power Automate!")
        else:
            print(f"Erro ao enviar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Falha na conexão: {e}")

# Exemplo de uso
if __name__ == '__main__':
    # Pode substituir por input() para digitar os números manualmente
    numbers = [10, 20, 30, 40, 50]  
    send_numbers_to_power_automate(numbers)