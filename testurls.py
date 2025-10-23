import requests

url = "https://raw.githubusercontent.com/user/repo/main/data.json"
response = requests.get(url)
data = response.json()  # Parse JSON directly

print(data)