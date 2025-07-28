# Générateur de programmes d'entraînement

Ce dossier contient une application web simple qui permet aux utilisateurs de renseigner des informations personnelles (âge, taille, poids et accès à du matériel) afin de générer un programme d'entraînement personnalisé à l'aide de l'API ChatGPT. Le site est monétisé via des publicités Google AdSense (non incluses par défaut) et des liens affiliés que vous pourrez ajouter vous‑même.

## Prérequis

- Python 3.10 ou supérieur.
- Une clé API OpenAI valide : définissez la variable d'environnement `OPENAI_API_KEY` avec votre clé pour activer la génération de programmes via ChatGPT.
- (Optionnel) Un compte Google AdSense et des liens affiliés pour la monétisation.

## Installation

1. **Installez les dépendances Python** :

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Définissez votre clé OpenAI** :

```bash
export OPENAI_API_KEY="votre_clé_api_openai"
```

3. **Lancez l'application** :

```bash
python app.py
```

L'application s'exécutera par défaut sur <http://localhost:5000>.

## Structure du projet

- `app.py` : serveur Flask qui gère les requêtes et communique avec l'API OpenAI.
- `requirements.txt` : dépendances Python nécessaires.
- `templates/index.html` : page principale contenant le formulaire et les sections de résultats.
- `static/css/style.css` : styles pour le site.
- `static/js/main.js` : logique côté client pour envoyer les informations et afficher les résultats.
- `static/data/exercises.json` : liste d'exercices avec noms et noms de fichiers d'images. Vous pouvez modifier cette liste ou y ajouter de nouveaux exercices.
- `static/images/placeholder.jpg` : image par défaut utilisée si aucune image n'est fournie pour un exercice.
- `static/images/exercises/` : dossier où vous devez placer vos propres images pour illustrer les exercices. Les noms de fichiers doivent correspondre aux champs `image` dans `exercises.json`.

## Formulaire : salle de sport et équipement

Le formulaire de la page d’accueil permet désormais de préciser si l'utilisateur s'entraîne en **salle de sport** ou **à domicile** :

- Si la case « Oui » est sélectionnée pour « Êtes‑vous en salle de sport ? », le programme généré part du principe que toutes sortes d'équipements (machines, haltères, barre de traction, etc.) sont disponibles.
- Si la case « Non » est sélectionnée, une liste de cases à cocher apparaît. L'utilisateur peut y indiquer quels équipements il possède (haltères, barre de traction, bandes élastiques, kettlebell, corde à sauter, tapis de sol). Cette liste peut être adaptée selon vos besoins en modifiant le HTML dans `templates/index.html`.

Ces informations sont envoyées au serveur pour adapter le prompt envoyé à l'API OpenAI en conséquence. Si aucun équipement n'est sélectionné à domicile, le programme proposera des exercices au poids du corps.

## Personnalisation des liens affiliés

Le fichier `app.py` contient une liste `PRODUCT_SUGGESTIONS` avec plusieurs produits :

```python
PRODUCT_SUGGESTIONS = [
    {
        "name": "Tapis de yoga antidérapant",
        "description": "Idéal pour les étirements et les exercices au sol.",
        "link": "#"  # Remplacez ce lien par votre lien affilié
    },
    ...
]
```

Pour chaque produit, remplacez la valeur du champ `link` par votre propre lien affilié. Les produits seront affichés sous forme de liste cliquable sur la page de résultats.

## Insertion du code Google AdSense

Dans le fichier `templates/index.html`, une section est réservée pour le code AdSense :

```html
<section class="ads-section">
    <!-- Insérez ici le code d'annonce Google AdSense -->
    <!-- Exemple: -->
    <!-- <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script> -->
    <!-- <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-xxxxxxxxxxxxxxxx" data-ad-slot="xxxxxxxxxx" data-ad-format="auto" data-full-width-responsive="true"></ins> -->
    <!-- <script>(adsbygoogle = window.adsbygoogle || []).push({});</script> -->
</section>
```

Remplacez cette partie par votre script d'annonce fourni par Google AdSense.

## Modification de la liste des exercices

La liste des exercices est définie dans `static/data/exercises.json`. Chaque entrée contient un nom et un nom de fichier d'image :

```json
{
  "name": "Pompes",
  "image": "pompes.jpg"
},
```

Pour chaque exercice, placez une image correspondante dans `static/images/exercises/` avec le nom indiqué. Si vous ne fournissez pas d'image, l'image par défaut `placeholder.jpg` sera utilisée.

## Notes importantes

- Ce site est fourni à des fins éducatives et doit être adapté à vos besoins avant d'être mis en production.
- Assurez‑vous de respecter la réglementation sur la collecte des données personnelles (notamment le RGPD en Europe).
- Les plans d'entraînement générés sont fournis à titre indicatif et ne remplacent pas l'avis d'un professionnel de santé ou d'un coach sportif qualifié.