import requests

response=requests.post("http://127.0.0.1:5000/users/login/",json={
    "email": "akash2005k26kaniyur1@gmail.com",
    "password": "pass143"
})
print(response.text)