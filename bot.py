import requests
import random
import time
from bs4 import BeautifulSoup

WEBHOOK_URL = "https://discord.com/api/webhooks/1484555324810723398/5C_TiGKAdL0HlR6bfHOHPRyhVANsTuxvAplD0F3yDps8HTm-qd358cVP7tR5dCabOVIN"

# Liste de pages (tu peux en ajouter)
URLS = [
    "https://www.hacoo.fr/",
    "https://www.hacoo.fr/category/homme",
    "https://www.hacoo.fr/category/femme"
]

# éviter les doublons
deja_envoyes = set()

def envoyer_discord(nom, prix, image, lien):
    data = {
        "embeds": [
            {
                "title": nom,
                "url": lien,
                "description": f"💸 {prix}",
                "image": {"url": image},
                "color": 5814783
            }
        ]
    }

    requests.post(WEBHOOK_URL, json=data)

def scraper_produits():
    url = random.choice(URLS)
    print(f"Scraping: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    produits = []

    # ⚠️ À adapter si besoin (structure du site)
    items = soup.find_all("a")

    for item in items:
        try:
            lien = item.get("href")

            if not lien or "/product" not in lien:
                continue

            nom = item.get_text().strip()
            if not nom or len(nom) < 5:
                continue

            image_tag = item.find("img")
            if not image_tag:
                continue

            image = image_tag.get("src")

            # prix approximatif (souvent dans le texte)
            prix = "Voir sur le site"

            full_link = "https://www.hacoo.fr" + lien

            if full_link in deja_envoyes:
                continue

            produits.append({
                "nom": nom,
                "prix": prix,
                "image": image,
                "lien": full_link
            })

        except:
            continue

    return produits

def main():
    while True:
        produits = scraper_produits()

        if not produits:
            print("Aucun produit trouvé...")
        else:
            produit = random.choice(produits)

            envoyer_discord(
                produit["nom"],
                produit["prix"],
                produit["image"],
                produit["lien"]
            )

            deja_envoyes.add(produit["lien"])

            print(f"Envoyé : {produit['nom']}")

        print("⏳ Attente 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    main()
