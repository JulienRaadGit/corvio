import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import tempfile

try:
    from openai import OpenAI
    client = OpenAI()
except ImportError:
    client = None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

CORS(app)  # allow all cross‑origin requests

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')

# In-memory storage for user workout plans (in production, use a database)
user_workout_plans = {}

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

def get_google_flow():
    """Create Google OAuth flow"""
    client_secrets = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:5000/callback"]
        }
    }
    
    flow = Flow.from_client_config(
        client_secrets,
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    flow.redirect_uri = "http://localhost:5000/callback"
    return flow

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
        f"Le programme doit être réparti sur 7 jours de la semaine et pour chaque jour, "
        f"décrire plusieurs exercices ou indiquer 'Repos' si c'est un jour de repos. Le format de sortie doit être exclusivement du JSON valide sans explication ni balise de code. "
        f"Structure du JSON : un objet avec une clé 'jours' contenant un tableau de 7 éléments. Chaque entrée du tableau représente un jour et doit "
        f"contenir au moins les clés 'nomJour' (par exemple 'Lundi', 'Mardi', etc.), 'type' ('workout' ou 'rest'), et 'exercices'. "
        f"La clé 'exercices' est un tableau d'objets (vide si type='rest'). "
        f"Chaque exercice doit avoir les clés suivantes : 'nom' (nom de l'exercice), 'series' (nombre de séries), 'repetitions' (nombre de répétitions, laisser vide ou null "
        f"si l'exercice est basé sur la durée), et 'duree_minutes' (durée en minutes si applicable, sinon null). Utilisez seulement ces clés. "
        f"Assurez‑vous que le JSON retourné soit strictement conforme à cette structure pour qu'il puisse être analysé par un programme."
    )

    # Si la bibliothèque openai n'est pas disponible, renvoyer un texte par défaut.
    if client is None:
        # Exemple de sortie JSON lorsque la bibliothèque openai n'est pas disponible
        example = {
            "jours": [
                {
                    "nomJour": "Lundi",
                    "type": "workout",
                    "exercices": [
                        {"nom": "Pompes", "series": 3, "repetitions": 12, "duree_minutes": None},
                        {"nom": "Squats", "series": 3, "repetitions": 15, "duree_minutes": None},
                        {"nom": "Planche", "series": 3, "repetitions": None, "duree_minutes": 1}
                    ]
                },
                {
                    "nomJour": "Mardi",
                    "type": "workout",
                    "exercices": [
                        {"nom": "Fentes", "series": 3, "repetitions": 12, "duree_minutes": None},
                        {"nom": "Gainage (Planche)", "series": 3, "repetitions": None, "duree_minutes": 1}
                    ]
                },
                {
                    "nomJour": "Mercredi",
                    "type": "rest",
                    "exercices": []
                },
                {
                    "nomJour": "Jeudi",
                    "type": "workout",
                    "exercices": [
                        {"nom": "Burpees", "series": 3, "repetitions": 10, "duree_minutes": None},
                        {"nom": "Mountain Climbers", "series": 3, "repetitions": None, "duree_minutes": 2}
                    ]
                },
                {
                    "nomJour": "Vendredi",
                    "type": "workout",
                    "exercices": [
                        {"nom": "Dips", "series": 3, "repetitions": 8, "duree_minutes": None},
                        {"nom": "Lunges", "series": 3, "repetitions": 12, "duree_minutes": None}
                    ]
                },
                {
                    "nomJour": "Samedi",
                    "type": "workout",
                    "exercices": [
                        {"nom": "Jumping Jacks", "series": 3, "repetitions": None, "duree_minutes": 3},
                        {"nom": "High Knees", "series": 3, "repetitions": None, "duree_minutes": 2}
                    ]
                },
                {
                    "nomJour": "Dimanche",
                    "type": "rest",
                    "exercices": []
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
                    "type": "workout",
                    "exercices": [
                        {"nom": "Pompes", "series": 3, "repetitions": 12, "duree_minutes": None},
                        {"nom": "Squats", "series": 3, "repetitions": 15, "duree_minutes": None}
                    ]
                }
            ]
        }
        return json.dumps(example, ensure_ascii=False)
    # Configure la clé API pour OpenAI.
    if client is None:
        return json.dumps({"jours": []}, ensure_ascii=False)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un coach sportif professionnel."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        workout = response.choices[0].message.content
        return workout.strip()

    except Exception as e:
        # En cas d'erreur, retourner un message informatif.
        return f"Une erreur est survenue lors de la génération du programme d'entraînement: {str(e)}"

@app.route('/')
def index():
    # Page principale. Rend le formulaire et la liste d'exercices.
    return render_template('index.html', user=session.get('user'))

@app.route('/workout-plan')
def workout_plan():
    """Page showing the current user's workout plan"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['sub']
    current_plan = user_workout_plans.get(user_id, None)
    
    return render_template('workout_plan.html', 
                         user=session['user'], 
                         workout_plan=current_plan)

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """Handle Google OAuth callback"""
    flow = get_google_flow()
    flow.fetch_token(authorization_response=request.url)
    
    if not session['state'] == request.args['state']:
        return redirect(url_for('index'))
    
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, requests.Request(), GOOGLE_CLIENT_ID
    )
    
    session['user'] = {
        'sub': id_info['sub'],
        'email': id_info['email'],
        'name': id_info.get('name', ''),
        'picture': id_info.get('picture', '')
    }
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

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
    
    # Save workout plan for logged-in user
    if 'user' in session:
        user_id = session['user']['sub']
        try:
            plan_data = json.loads(plan)
            user_workout_plans[user_id] = plan_data
        except:
            pass  # If plan is not valid JSON, don't save it
    
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