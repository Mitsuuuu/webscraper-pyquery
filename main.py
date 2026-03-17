from tqdm import tqdm
import requests
from pyquery import PyQuery as pq
1
from Scraping.Loop import collection_loop

zahl = int (input("Aktion auswählen:"))
match zahl:
    case 1:
        print(collection_loop())








