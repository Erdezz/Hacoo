import asyncio
import random
import requests
from playwright.async_api import async_playwright

WEBHOOK_URL = "https://discord.com/api/webhooks/1484555324810723398/5C_TiGKAdL0HlR6bfHOHPRyhVANsTuxvAplD0F3yDps8HTm-qd358cVP7tR5dCabOVIN"  # Remplace par ton webhook Discord

# Liste des pages à scraper
URLS = [
    "https://www.hacoo.fr/category/femme",
    "https://www.hacoo.fr/category/homme",
    "https://www.hacoo.fr/category/nouveautes"
]

async def get_produits():
    async with async_playwright() as p:
        browser = await p.chromium.launch()  # Lance Chromium en mode headless
        page = await browser.new_page()

        url = random.choice(URLS)  # Choisir une page aléatoire à scraper
        print(f"Chargement de la page : {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)  # Attendre 5 secondes que la page charge

        produits = []

        # Sélecteur CSS des produits - à adapter si nécessaire
        items = await page.query_selector_all("li.product-grid-item")

        for item in items:
            try:
                nom = await item.query_selector_eval("h3.product-name", "el => el.innerText")
                prix = await item.query_selector_eval(".product-price", "el => el.innerText")
                image = await item.query_selector_eval("img", "el => el.src")
                lien = await item.query_selector_eval("a", "el => el.href")

                # Maintenant, récupère le lien affilié
                if lien:
                    aff_link = await get_affiliate_link(lien)
                    produits.append({
                        "nom": nom.strip(),
                        "prix": prix.strip(),
                        "image": image,
                        "lien": aff_link
                    })
            except Exception as e:
                print(f"Erreur lors du traitement du produit : {e}")
                continue

        await browser.close()
        return produits

async def get_affiliate_link(produit_url):
    """
    Cette fonction prend l'URL du produit, et la convertit en lien affilié.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Ouvrir la page du produit
        await page.goto(produit_url)
        await page.wait_for_timeout(2000)  # Attente que la page se charge
        
        # Clique sur le bouton de partage ou un autre élément pour obtenir le lien affilié
        # Adapter le sélecteur en fonction de la structure HTML de la page produit
        partage_button = await page.query_selector('button[class="share-button-class"]')  # Remplace par le sélecteur réel
        if partage_button:
            await partage_button.click()  # Clique sur "Partager"
        
        # Récupérer le lien affilié qui pourrait être dans un élément HTML
        await page.wait_for_selector('div[class="affiliation-link-class"]')  # Remplace par le bon sélecteur
        aff_link = await page.query_selector_eval('div[class="affiliation-link-class"]', "el => el.innerText")
        
        await browser.close()
        return aff_link.strip() if aff_link else produit_url  # Si pas de lien affilié, retourne l'URL du produit

def envoyer_discord(nom, prix, image, lien):
    data = {
        "embeds": [{
            "title": nom,
            "url": lien,
            "description": prix,
            "image": {"url": image},
            "color": 5814783  # Couleur pour l'embed
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
