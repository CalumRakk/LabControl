import requests

headers = {
    "Content-Type": "application/json",
}

# start_browser = {"action": "Start"}
go_to_url = {
    "action": "go_to_url",
    "url": "https://app.aluracursos.com/formacion-desarrollo-personal-grupo7-one",
}

# response = requests.get(
#     "http://127.0.0.1:8000/host/api/browser", headers=headers, data=start_browser
# )

response = requests.get(
    "http://127.0.0.1:8000/host/api/status/?format=json&random=${Math.random()}",
    headers=headers,
    json=go_to_url,
)
print(response.text)
