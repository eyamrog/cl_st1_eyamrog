import requests

response = requests.get("https://httpbin.org/headers")
print(response.text)  # This returns your request headers
