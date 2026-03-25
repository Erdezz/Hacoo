import asyncio
import random
import requests
from playwright.async_api import async_playwright

# Remplace par ton webhook Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1484555324810723398/5C_TiGKAdL0HlR6bfHOHPRyhVANsTuxvAplD0F3yDps8HTm-qd358cVP7tR5dCabOVIN"

async def get_produits():
    async with async_playwright() as p:
        browser = await p.chromium.launch()  # Lance Chromium en mode headless
        page = await browser.new_page()

        url = random.choice(URLS)  # Choisir une page aléatoire à scraper
        print(f"Chargement de la page : {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)  # Attendre 5 secondes que la page charge

        produits = []

        # Sélecteur CSS des produits - adapte-le à la structure de la page
        items = await page.query_selector_all("div.product-item")  # Adapté à la structure du site

        for item in items:
            try:
                # Récupérer les informations du produit (nom, prix, etc.)
                nom = await item.query_selector_eval("h3.product-name", "el => el.innerText")
                prix = await item.query_selector_eval(".product-price", "el => el.innerText")
                image = await item.query_selector_eval("img", "el => el.src")
                lien = await item.query_selector_eval("a", "el => el.href")

                if lien:
                    aff_link = await get_affiliate_link(lien)  # Récupérer le lien affilié
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
    Cette fonction prend l'URL du produit et retourne le lien affilié.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Accéder à la page produit
        await page.goto(produit_url)
        await page.wait_for_timeout(2000)  # Attente pour que la page se charge correctement

        # Clique sur le bouton de partage ou tout autre mécanisme pour obtenir le lien affilié
        # Adaptation nécessaire : modifier le sélecteur pour le bouton "Partager"
        partage_button = await page.query_selector('button[class="share-button-class"]')  # Change ce sélecteur
        if partage_button:
            await partage_button.click()  # Clique pour générer le lien affilié

        # Attente que le lien affilié apparaisse dans un champ input ou autre élément
        await page.wait_for_selector('input[class="affiliation-link-class"]')  # Modifie ce sélecteur
        aff_link = await page.query_selector_eval('input[class="affiliation-link-class"]', "el => el.value")

        await browser.close()
        return aff_link.strip() if aff_link else produit_url  # Si le lien affilié n'est pas trouvé, retourne l'URL classique

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
        print(f"Produit envoyé sur Discord : {nom}")
    else:
        print(f"Erreur webhook : {response.status_code} {response.text}")

async def main():
    produits = await get_produits()
    if not produits:
        print("Aucun produit trouvé.")
        return
    produit = random.choice(produits)
    envoyer_discord(produit["nom"], produit["prix"], produit["image"], produit["lien"])

if __name__ == "__main__":
    asyncio.run(main())
