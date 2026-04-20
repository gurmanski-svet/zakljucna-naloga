import requests

API_KEYS = [
    "32be0b921f2a4e7fac0f85279c03b8cb",
    "6fea24f6376a45eb9033908b8bbc7579",
    "c2349e0991734b2b9b61908591c4aaab"
]

current_key_index = 0

def get_api_key():
    global current_key_index
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key

def api_request(url_base):
    for key in API_KEYS:
        url = f"{url_base}&apiKey={key}"
        response = requests.get(url)
        
        try:
            data = response.json()
        except:
            continue

        if "error" in data:
            continue

        if response.status_code == 200 and "status" not in data:
            return data

    return {"error": "Vsi API ključi so porabljeni"}