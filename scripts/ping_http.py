import requests, os


# data = {"foo": "bar"}
# response = requests.get("http://localhost:8000/ping", json=data)
# print(response.status_code)
# print(response.json())

# url = "https://planned-calendars-eyes-andrews.trycloudflare.com"
# response = requests.get(f"{url}/ping", json=data)
# print(response.status_code)
# print(response.json())
# exit()

CF_ACCESS_CLIENT_ID: str = os.environ.get("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET: str = os.environ.get("CF_ACCESS_CLIENT_SECRET")
headers = {
    "CF-Access-Client-Id": CF_ACCESS_CLIENT_ID,
    "CF-Access-Client-Secret": CF_ACCESS_CLIENT_SECRET
}
data = {"foo": "bar"}
response = requests.get("https://iot.brandonfremin.com/ping", headers=headers, json=data)
print(response.text)
