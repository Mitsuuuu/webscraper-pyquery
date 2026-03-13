from Scraping.PageLoop import page_loop


zahl = int (input("Aktion auswählen:"))
match zahl:
    case 1:
        names = page_loop()
        print(names)