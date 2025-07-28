import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

try:
    import openai
except ImportError:
    openai = None  # We handle missing dependency gracefully


app = Flask(__name__)
CORS(app)  # allow all cross‑origin requests

# Load product suggestions from a hard‑coded list.
PRODUCT_SUGGESTIONS = [
    {
        "name": "Tapis de yoga antidérapant",
        "description": "Idéal pour les étirements et les exercices au sol.",
        "link": "#"  # Remplacez ce lien par votre lien affilié
    },
    {
        "name": "Haltères ajustables",
        "description": "Parfaites pour varier l'intensité de vos entraînements.",
        "link": "#"  # Remplacez ce lien par votre lien affilié
    },
    {
        "name": "Bande de résistance",
        "description": "Accessoire polyvalent pour travailler l'ensemble du corps.",
        "link": "#"  # Remplacez ce lien par votre lien affilié
    },
    {
        "name": "Rouleau de massage en mousse",
        "description": "Pour la récupération musculaire après l'entraînement.",
        "link": "#"  # Remplacez ce lien par votre lien affilié
    }
]


def generate_workout_plan(height: str, weight: str, age: str, gym: bool, equipment_list: list[str]) -> str:
    """
    Utilise l'API OpenAI pour générer un plan d'entraînement personnalisé en français.

    :param height: taille de l'utilisateur en centimètres (string pour simplicité)
    :param weight: poids de l'utilisateur en kilogrammes (string)
    :param age: âge de l'utilisateur (string)
    :param gym: boolean indiquant si l'utilisateur est en salle de sport (accès complet à tous les équipements)
    :param equipment_list: liste de chaînes décrivant l'équipement disponible si l'utilisateur n'est pas en salle de sport
    :return: texte du plan d'entraînement généré
    """
    # Construire la description de l'équipement
    if gym:
        equipment_text = (
            "en salle de sport avec accès à une grande variété d'équipements (haltères, machines, barre de traction, etc.)"
        )
    else:
        if equipment_list:
            # Formater la liste en français
            formatted = ", ".join(equipment_list)
            equipment_text = f"à domicile avec accès aux équipements suivants : {formatted}"
        else:
            equipment_text = "à domicile avec aucun équipement spécifique"

    # Prépare le prompt pour ChatGPT.
    prompt = (
        f"Vous êtes un coach sportif professionnel. Créez un programme d'entraînement structuré en français "
        f"pour une personne de {age} ans, mesurant {height} cm et pesant {weight} kg, {equipment_text}. "
        f"Le programme doit être réparti sur plusieurs jours de la semaine (par exemple 5 ou 7 jours) et pour chaque jour, "
        f"décrire plusieurs exercices. Le format de sortie doit être exclusivement du JSON valide sans explication ni balise de code. "
        f"Structure du JSON : un objet avec une clé 'jours' contenant un tableau. Chaque entrée du tableau représente un jour et doit "
        f"contenir au moins les clés 'nomJour' (par exemple 'Lundi', 'Mardi', etc.) et 'exercices'. La clé 'exercices' est un tableau d'objets. "
        f"Chaque exercice doit avoir les clés suivantes : 'nom' (nom de l'exercice), 'series' (nombre de séries), 'repetitions' (nombre de répétitions, laisser vide ou null "
        f"si l'exercice est basé sur la durée), et 'duree_minutes' (durée en minutes si applicable, sinon null). Utilisez seulement ces clés. "
        f"Assurez‑vous que le JSON retourné soit strictement conforme à cette structure pour qu'il puisse être analysé par un programme."
    )

    # Si la bibliothèque openai n'est pas disponible, renvoyer un texte par défaut.
    if openai is None:
        # Exemple de sortie JSON lorsque la bibliothèque openai n'est pas disponible
        example = {
            "jours": [
                {
                    "nomJour": "Lundi",
                    "exercices": [
                        {"nom": "Pompes", "series": 3, "repetitions": 12, "duree_minutes": None},
                        {"nom": "Squats", "series": 3, "repetitions": 15, "duree_minutes": None},
                        {"nom": "Planche", "series": 3, "repetitions": None, "duree_minutes": 1}
                    ]
                },
                {
                    "nomJour": "Mardi",
                    "exercices": [
                        {"nom": "Fentes", "series": 3, "repetitions": 12, "duree_minutes": None},
                        {"nom": "Gainage (Planche)", "series": 3, "repetitions": None, "duree_minutes": 1}
                    ]
                }
            ]
        }
        return json.dumps(example, ensure_ascii=False)

    # Récupère la clé API depuis les variables d'environnement.
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        example = {
            "jours": [
                {
                    "nomJour": "Lundi",
                    "exercices": [
                        {"nom": "Pompes", "series": 3, "repetitions": 12, "duree_minutes": None},
                        {"nom": "Squats", "series": 3, "repetitions": 15, "duree_minutes": None}
                    ]
                }
            ]
        }
        return json.dumps(example, ensure_ascii=False)
    # Configure la clé API pour OpenAI.
    openai.api_key = api_key
    try:
        # Utiliser par défaut le modèle GPT‑4.1 mini si disponible. Ce nom peut être adapté selon les modèles
        # disponibles sur votre compte (exemple : "gpt-4.1-mini" ou "gpt-4.1-mini-2025-04-14").
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un coach sportif professionnel."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        workout = response.choices[0].message['content']
        return workout.strip()
    except Exception as e:
        # En cas d'erreur, retourner un message informatif.
        return f"Une erreur est survenue lors de la génération du programme d'entraînement: {str(e)}"


@app.route('/')
def index():
    # Page principale. Rend le formulaire et la liste d'exercices.
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json(force=True)
    height = data.get('height', '')
    weight = data.get('weight', '')
    age = data.get('age', '')
    gym = data.get('gym', False)
    equipment_list = data.get('equipmentList', [])

    # Convert list elements to strings just in case
    if not isinstance(equipment_list, list):
        equipment_list = []
    equipment_list = [str(item) for item in equipment_list]

    plan = generate_workout_plan(height, weight, age, gym, equipment_list)
    return jsonify({
        'plan': plan,
        'products': PRODUCT_SUGGESTIONS
    })


@app.route('/static/data/exercises.json')
def exercises():
    # Retourne la liste des exercices sous forme de JSON pour le front.
    data_path = os.path.join(app.root_path, 'static', 'data', 'exercises.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            exercises_data = json.load(f)
    except Exception:
        exercises_data = []
    return jsonify(exercises_data)


if __name__ == '__main__':
    # Lance l'application Flask.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)