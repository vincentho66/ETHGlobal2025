

import json
import requests
API_KEY = "SzUw03Hl7YOLHXIUKfNQ3COn0DKldk3Q"
BASE_URL = "https://api.1inch.dev/token"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "accept": "application/json"
}

def get_1inch_token_list(chain_id, provider="1inch"):
    endpoint = f"{BASE_URL}/v1.2/{chain_id}/token-list"
    params = {
        "provider": provider,
    }
    response = requests.get(endpoint, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get 1inch token list. Status code: {response.status_code}")
        return None
    
jsons = get_1inch_token_list(137)
print(json.dumps(jsons))