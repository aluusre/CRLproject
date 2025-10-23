import requests

#url = "https://raw.githubusercontent.com/user/repo/main/data.json"
url = "https://github.com/aluusre/CRLproject/blob/main/CRLurls2.json"
response = requests.get(url)
data = response.json()  # Parse JSON directly

print(data)
