import requests

url = "https://newsmaker.md/ru/category/news"
response = requests.get(url)

print("Wait for answer!")
print(response.status_code)  # Проверка кода ответа (200 - всё ок)
print(response.text)         # Просмотр содержимого
