import asyncio
import random
import requests
from playwright.async_api import async_playwright

WEBHOOK_URL = "https://discord.com/api/webhooks/1484555324810723398/5C_TiGKAdL0HlR6bfHOHPRyhVANsTuxvAplD0F3yDps8HTm-qd358cVP7tR5dCabOVIN"

URLS = [
    "https://www.hacoo.fr/category/femme",
    "https://www.hacoo.fr/category/homme",
    "https://www.hacoo.fr/category/nouveautes"
]

async def get_produits():
    async with async_playwright() as p:
        browser = await p.chromium.launch()  # headless par défaut
        page = await browser.new_page()

        url = random.choice(URLS)
        print(f"Chargement de la page : {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)  # attendre 5 sec que JS charge

        produits = []

        # Sélecteur CSS des produits - à adapter si nécessaire
        items = await page.query_selector_all("li.product-grid-item")

        for item in items:
            try:
                nom = await item.query_selector_eval("h3.product-name", "el => el.innerText")
                prix = await item.query_selector_eval(".product-price", "el => el.innerText")
                image = await item.query_selector_eval("img", "el => el.src")
                lien = await item.query_selector_eval("a", "el => el.href")

                produits.append({
                    "nom": nom.strip(),
                    "prix": prix.strip(),
                    "image": image,
                    "lien": lien
                })
            except Exception:
                continue

        await browser.close()
        return produits

def envoyer_discord(nom, prix, image, lien):
    data = {
        "embeds": [{
            "title": nom,
            "url": lien,
            "description": prix,
            "image": {"url": image},
            "color": 5814783
        }]
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"Envoyé sur Discord : {nom}")
    else:
        print(f"Erreur webhook: {response.status_code} {response.text}")

async def main():
    produits = await get_produits()
    if not produits:
        print("Aucun produit trouvé")
        return
    produit = random.choice(produits)
    envoyer_discord(produit["nom"], produit["prix"], produit["image"], produit["lien"])

if __name__ == "__main__":
    asyncio.run(main())
