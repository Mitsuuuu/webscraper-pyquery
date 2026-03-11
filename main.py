import requests
from pyquery import PyQuery as pq

r = requests.get("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
doc = pq(r.content)
print(doc("h1").text())
print(doc("p.price_color").text())
print(doc("p.instock.availability").text())