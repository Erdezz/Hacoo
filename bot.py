import requests
import random
import time
from bs4 import BeautifulSoup

# Remplace par ton webhook Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1484555324810723398/5C_TiGKAdL0HlR6bfHOHPRyhVANsTuxvAplD0F3yDps8HTm-qd358cVP7tR5dCabOVIN"

# Liste des pages à scraper
URLS = [
    "https://www.hacoo.fr/",
    "https://www.hacoo.fr/category/homme",
    "https://www.hacoo.fr/category/femme"
]

# Pour éviter d'envoyer plusieurs fois le même produit
deja_envoyes = set()

def envoyer_discord(nom, prix, image, lien):
    """
    Fonction qui envoie un message avec un embed à Discord via Webhook.
    """
    data = {
        "embeds": [
            {
                "title": nom,
                "url": lien,
                "description": f"💸 {prix}",
                "image": {"url": image},
                "color": 5814783  # Couleur pour l'embed
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"Produit envoyé : {nom}")
    else:
        print(f"Erreur en envoyant le produit : {nom}")

def scraper_produits():
    """
    Fonction pour scraper les produits depuis les URLs définies.
    """
    url = random.choice(URLS)  # Choisit une page aléatoire à scraper
    print(f"Scraping de la page : {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        # Demande HTTP pour récupérer la page
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return []

    produits = []

    # Scraper tous les liens de produits (adapte selon le site)
    items = soup.find_all("a", href=True)
    
    for item in items:
        try:
            lien = item.get("href")
            if "/product" not in lien:
                continue

            # Extraire les détails du produit
            nom = item.get_text().strip()
            if not nom or len(nom) < 5:
                continue

            image_tag = item.find("img")
            if not image_tag:
                continue

            image = image_tag.get("src")
            prix = "Voir sur le site"  # Change si tu veux extraire le prix

            full_link = "https://www.hacoo.fr" + lien

            # Éviter d'envoyer les produits déjà envoyés
            if full_link in deja_envoyes:
                continue

            produits.append({
                "nom": nom,
                "prix": prix,
                "image": image,
                "lien": full_link
            })

        except Exception as e:
            print(f"Erreur lors du traitement du produit : {e}")
            continue

    return produits

def main():
    """
    Fonction principale qui récupère un produit et l'envoie à Discord.
    """
    produits = scraper_produits()

    if not produits:
        print("Aucun produit trouvé.")
        return

    produit = random.choice(produits)  # Choisir un produit au hasard
    envoyer_discord(produit["nom"], produit["prix"], produit["image"], produit["lien"])

if __name__ == "__main__":
    main()
