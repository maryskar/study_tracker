import requests

url = "http://127.0.0.1:8000/users/"
data = {
    "username": "user1",
    "hashed_password": "somehashedpassword"
}

response = requests.post(url, json=data)

print("Status code:", response.status_code)
print("Response body:", response.json())
