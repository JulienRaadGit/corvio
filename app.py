import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from flask_session import Session
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import firestore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI()
except ImportError:
    client = None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

CORS(app)

# Mapping des exercices et jours pour compression
EXERCISE_MAPPING = {
    1: "Pompes", 2: "Squats", 3: "Fentes", 4: "Gainage (Planche)", 5: "Burpees",
    6: "Tractions", 7: "Dips", 8: "Mountain Climbers", 9: "Jumping Jacks", 10: "High Knees",
    11: "Curl biceps", 12: "Extensions triceps", 13: "Développé militaire", 14: "Rowing", 15: "Soulevé de terre",
    16: "Planche latérale", 17: "Crunchs", 18: "Mollets debout", 19: "Abduction des hanches", 20: "Course à pied",
    21: "Vélo", 22: "Natation", 23: "Marche", 24: "Étirements", 25: "Sauts sur place",
    26: "Kettlebell Swing", 27: "Corde à sauter", 28: "Tirage horizontal", 29: "Développé couché", 30: "Yoga"
}

# Exercices mesurés en temps (durée) plutôt qu'en répétitions
TIME_BASED_EXERCISES = {
    4: "Gainage (Planche)",      # Planche
    16: "Planche latérale",      # Planche latérale
    24: "Étirements",           # Étirements
    25: "Cardio",               # Cardio général
    20: "Course à pied",        # Course
    21: "Vélo",                 # Vélo
    22: "Natation",             # Natation
    23: "Marche"                # Marche
}

DAY_MAPPING = {1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi", 6: "Samedi", 7: "Dimanche"}

# Firebase configuration - using environment variables for security
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "corvio-bf0b0",
    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL', ''),
    "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL', '')
}

# Check if Firebase credentials are properly configured
firebase_initialized = False
missing_credentials = []

# Check for missing environment variables
if not FIREBASE_CONFIG['private_key_id']:
    missing_credentials.append('FIREBASE_PRIVATE_KEY_ID')
if not FIREBASE_CONFIG['private_key']:
    missing_credentials.append('FIREBASE_PRIVATE_KEY')
if not FIREBASE_CONFIG['client_email']:
    missing_credentials.append('FIREBASE_CLIENT_EMAIL')
if not FIREBASE_CONFIG['client_id']:
    missing_credentials.append('FIREBASE_CLIENT_ID')
if not FIREBASE_CONFIG['client_x509_cert_url']:
    missing_credentials.append('FIREBASE_CLIENT_CERT_URL')

# Initialize Firebase Admin SDK
if missing_credentials:
    print(f"⚠️  Firebase credentials missing: {', '.join(missing_credentials)}")
    print("Please set the following environment variables:")
    for cred in missing_credentials:
        print(f"  - {cred}")
    print("Firebase authentication will not work without these credentials.")
    db = None
else:
    try:
        cred = credentials.Certificate(FIREBASE_CONFIG)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        db = firestore.client()
        print("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization error: {e}")
        print("Firebase authentication will not work.")
        db = None

# In-memory storage for user workout plans
user_workout_plans = {}

# Load product suggestions
PRODUCT_SUGGESTIONS = [
    {
        "name": "Tapis de yoga antidérapant",
        "description": "Idéal pour les étirements et les exercices au sol.",
        "link": "#"
    },
    {
        "name": "Haltères ajustables",
        "description": "Parfaites pour varier l'intensité de vos entraînements.",
        "link": "#"
    },
    {
        "name": "Bande de résistance",
        "description": "Accessoire polyvalent pour travailler l'ensemble du corps.",
        "link": "#"
    },
    {
        "name": "Rouleau de massage en mousse",
        "description": "Pour la récupération musculaire après l'entraînement.",
        "link": "#"
    }
]

# Blog articles data (5 articles)
BLOG_ARTICLES = [
    {
        "id": "musculation-debutants",
        "title": "Guide complet de la musculation pour débutants",
        "category": "Musculation",
        "date": "15 Janvier 2024",
        "image": "strength-training.jpg",
        "excerpt": "Découvrez les bases essentielles de la musculation : exercices fondamentaux, techniques correctes et progression adaptée aux débutants.",
        "content": """
        <h2>Les bases de la musculation</h2>
        <p>La musculation est une discipline sportive qui vise à développer la force et la masse musculaire. Pour les débutants, il est essentiel de comprendre les principes fondamentaux avant de commencer.</p>
        
        <h3>Les exercices fondamentaux</h3>
        <ul>
            <li><strong>Pompes</strong> : Excellent exercice pour les pectoraux et les triceps</li>
            <li><strong>Squats</strong> : Indispensable pour les jambes et les fessiers</li>
            <li><strong>Gainage</strong> : Pour renforcer la ceinture abdominale</li>
        </ul>
        
        <h3>Techniques correctes</h3>
        <p>La qualité prime sur la quantité. Il est préférable de faire moins de répétitions avec une technique parfaite que l'inverse.</p>
        
        <h3>Progression adaptée</h3>
        <p>Commencez progressivement et augmentez l'intensité au fil des semaines. Votre corps a besoin de temps pour s'adapter.</p>
        """
    },
    {
        "id": "cardio-efficace",
        "title": "5 séances de cardio efficaces pour brûler les graisses",
        "category": "Cardio",
        "date": "12 Janvier 2024",
        "image": "cardio-workout.jpg",
        "excerpt": "Optimisez votre perte de poids avec ces entraînements cardio variés et intensifs, adaptés à tous les niveaux.",
        "content": """
        <h2>Le cardio pour perdre du poids</h2>
        <p>Le cardio est essentiel pour brûler des calories et améliorer votre condition cardiovasculaire. Voici 5 séances efficaces.</p>
        
        <h3>Séance 1 : HIIT (High Intensity Interval Training)</h3>
        <p>30 secondes d'effort intense suivies de 30 secondes de récupération, répété 10 fois.</p>
        
        <h3>Séance 2 : Course à pied</h3>
        <p>Commencez par 20 minutes de course à un rythme modéré.</p>
        
        <h3>Séance 3 : Vélo</h3>
        <p>45 minutes de vélo avec des variations d'intensité.</p>
        
        <h3>Séance 4 : Natation</h3>
        <p>30 minutes de nage libre pour un cardio complet.</p>
        
        <h3>Séance 5 : Marche rapide</h3>
        <p>1 heure de marche à un rythme soutenu.</p>
        """
    },
    {
        "id": "nutrition-sportive",
        "title": "Nutrition sportive : que manger avant et après l'entraînement",
        "category": "Nutrition",
        "date": "10 Janvier 2024",
        "image": "nutrition.jpg",
        "excerpt": "Maximisez vos performances et votre récupération grâce à une alimentation adaptée à vos objectifs sportifs.",
        "content": """
        <h2>L'importance de la nutrition sportive</h2>
        <p>Une alimentation adaptée peut faire la différence entre une séance moyenne et une séance exceptionnelle.</p>
        
        <h3>Avant l'entraînement</h3>
        <ul>
            <li><strong>2-3 heures avant</strong> : Repas complet avec glucides complexes</li>
            <li><strong>1 heure avant</strong> : Fruit ou barre énergétique</li>
            <li><strong>30 minutes avant</strong> : Hydratation suffisante</li>
        </ul>
        
        <h3>Après l'entraînement</h3>
        <ul>
            <li><strong>Dans les 30 minutes</strong> : Protéines et glucides simples</li>
            <li><strong>Dans les 2 heures</strong> : Repas équilibré</li>
        </ul>
        
        <h3>Hydratation</h3>
        <p>Buvez régulièrement avant, pendant et après l'effort pour maintenir vos performances.</p>
        """
    },
    {
        "id": "entrainement-domicile",
        "title": "Programme d'entraînement complet à domicile sans matériel",
        "category": "Entraînement",
        "date": "8 Janvier 2024",
        "image": "home-workout.jpg",
        "excerpt": "Restez en forme même sans salle de sport avec ce programme complet utilisant uniquement votre poids de corps.",
        "content": """
        <h2>L'entraînement à domicile</h2>
        <p>Pas besoin d'équipement coûteux pour se muscler et rester en forme. Votre corps est votre meilleur outil.</p>
        
        <h3>Programme complet</h3>
        <ul>
            <li><strong>Lundi</strong> : Haut du corps (pompes, dips, gainage)</li>
            <li><strong>Mardi</strong> : Bas du corps (squats, fentes, mollets)</li>
            <li><strong>Mercredi</strong> : Repos</li>
            <li><strong>Jeudi</strong> : Cardio (burpees, jumping jacks)</li>
            <li><strong>Vendredi</strong> : Corps complet</li>
            <li><strong>Samedi</strong> : Étirements et yoga</li>
            <li><strong>Dimanche</strong> : Repos</li>
        </ul>
        
        <h3>Exercices clés</h3>
        <p>Pompes, squats, gainage, burpees, mountain climbers, jumping jacks...</p>
        """
    },
    {
        "id": "recuperation-musculaire",
        "title": "Les secrets d'une récupération musculaire optimale",
        "category": "Récupération",
        "date": "5 Janvier 2024",
        "image": "recovery.jpg",
        "excerpt": "Découvrez les techniques et astuces pour accélérer votre récupération et éviter les blessures.",
        "content": """
        <h2>La récupération : clé du progrès</h2>
        <p>La récupération est aussi importante que l'entraînement lui-même. C'est pendant cette phase que vos muscles se reconstruisent.</p>
        
        <h3>Techniques de récupération</h3>
        <ul>
            <li><strong>Étirements</strong> : Après chaque séance</li>
            <li><strong>Hydratation</strong> : Buvez suffisamment d'eau</li>
            <li><strong>Sommeil</strong> : 7-9 heures par nuit</li>
            <li><strong>Massage</strong> : Avec un rouleau de mousse</li>
        </ul>
        
        <h3>Nutrition post-entraînement</h3>
        <p>Consommez des protéines dans les 30 minutes suivant votre séance pour optimiser la récupération.</p>
        """
    }
]

# Fonction pour récupérer un article par ID
def get_article_by_id(article_id):
    for article in BLOG_ARTICLES:
        if article['id'] == article_id:
            return article
    return None

def compress_workout_plan(plan_data):
    """Compresse un plan d'entraînement en remplaçant les noms par des IDs"""
    if not isinstance(plan_data, dict) or 'jours' not in plan_data:
        return plan_data
    
    # Mapping inverse pour trouver les IDs
    exercise_to_id = {v: k for k, v in EXERCISE_MAPPING.items()}
    day_to_id = {v: k for k, v in DAY_MAPPING.items()}
    
    compressed = {"j": []}  # "j" pour "jours"
    
    for day in plan_data['jours']:
        compressed_day = {
            "d": day_to_id.get(day.get('nomJour', ''), day.get('nomJour', '')),  # "d" pour "day"
            "t": 1 if day.get('type') == 'workout' else 0,  # "t" pour "type", 1=workout, 0=rest
            "e": []  # "e" pour "exercices"
        }
        
        if day.get('type') == 'workout' and day.get('exercices'):
            for exercise in day['exercices']:
                compressed_exercise = {
                    "n": exercise_to_id.get(exercise.get('nom', ''), exercise.get('nom', '')),  # "n" pour "nom"
                    "s": exercise.get('series', 0),  # "s" pour "series"
                    "r": exercise.get('repetitions'),  # "r" pour "repetitions"
                    "m": exercise.get('duree_minutes')  # "m" pour "minutes"
                }
                # Supprimer les valeurs nulles pour économiser l'espace
                compressed_exercise = {k: v for k, v in compressed_exercise.items() if v is not None}
                compressed_day["e"].append(compressed_exercise)
        
        compressed["j"].append(compressed_day)
    
    return compressed

def decompress_workout_plan(compressed_data):
    """Décompresse un plan d'entraînement compressé"""
    if not isinstance(compressed_data, dict) or 'j' not in compressed_data:
        return compressed_data
    
    decompressed = {"jours": []}
    
    for day in compressed_data['j']:
        decompressed_day = {
            "nomJour": DAY_MAPPING.get(day.get('d'), str(day.get('d', ''))),
            "type": "workout" if day.get('t', 0) == 1 else "rest",
            "exercices": []
        }
        
        if day.get('t', 0) == 1 and day.get('e'):
            for exercise in day['e']:
                decompressed_exercise = {
                    "nom": EXERCISE_MAPPING.get(exercise.get('n'), str(exercise.get('n', ''))),
                    "series": exercise.get('s', 0),
                    "repetitions": exercise.get('r'),
                    "duree_minutes": exercise.get('m')
                }
                decompressed_day["exercices"].append(decompressed_exercise)
        
        decompressed["jours"].append(decompressed_day)
    
    return decompressed

def generate_workout_plan(height: str, weight: str, age: str, gym: bool, equipment_list: list[str], 
                         difficulty: str = "intermediate", max_session_duration: int = None, max_workout_days: int = None) -> str:
    """
    Utilise l'API OpenAI pour générer un plan d'entraînement personnalisé en format compressé.
    """
    if gym:
        equipment_text = "en salle de sport avec accès à une grande variété d'équipements"
    else:
        if equipment_list:
            formatted = ", ".join(equipment_list)
            equipment_text = f"à domicile avec : {formatted}"
        else:
            equipment_text = "à domicile sans équipement"

    # Construire le texte de difficulté
    difficulty_text = f"niveau {difficulty}"
    
    # Construire les contraintes de durée et jours
    constraints = []
    if max_session_duration:
        constraints.append(f"durée maximale de session: {max_session_duration} minutes")
    if max_workout_days:
        constraints.append(f"maximum {max_workout_days} jours d'entraînement par semaine")
    
    constraints_text = ""
    if constraints:
        constraints_text = f" Contraintes: {', '.join(constraints)}."

    # Liste des exercices disponibles avec leurs IDs
    exercise_list = "\n".join([f"{k}: {v}" for k, v in EXERCISE_MAPPING.items()])
    
    # Informations sur les exercices mesurés en temps
    time_exercises = "\n".join([f"- {v} (ID: {k})" for k, v in TIME_BASED_EXERCISES.items()])
    
    prompt = (
        f"Créez un programme d'entraînement pour: {age} ans, {height}cm, {weight}kg, {equipment_text}, {difficulty_text}.{constraints_text} "
        f"UTILISEZ UNIQUEMENT ce format JSON compressé et ces exercices:\n{exercise_list}\n\n"
        f"IMPORTANT - Exercices mesurés en TEMPS (utilisez 'm' pour minutes):\n{time_exercises}\n\n"
        f"Format JSON OBLIGATOIRE (sans explication, sans ```json):\n"
        f'{{"j":[{{"d":1,"t":1,"e":[{{"n":1,"s":3,"r":12}},{{"n":4,"s":3,"m":1}}]}},{{"d":2,"t":0,"e":[]}}]}}\n\n'
        f"Légende: j=jours, d=jour(1-7), t=type(1=workout,0=rest), e=exercices, n=nom(ID), s=séries, r=répétitions, m=minutes\n"
        f"RÈGLES: Pour les exercices de gainage, cardio et étirements, utilisez 'm' (minutes). Pour les autres, utilisez 'r' (répétitions).\n"
        f"Choisissez les exercices selon l'équipement disponible et le niveau de difficulté. RETOURNEZ SEULEMENT LE JSON."
    )

    if client is None:
        # Version compressée de l'exemple par défaut
        example = {
            "j": [
                {"d": 1, "t": 1, "e": [{"n": 1, "s": 3, "r": 12}, {"n": 2, "s": 3, "r": 15}]},
                {"d": 2, "t": 1, "e": [{"n": 3, "s": 3, "r": 12}, {"n": 4, "s": 3, "m": 1}]},
                {"d": 3, "t": 0, "e": []},
                {"d": 4, "t": 1, "e": [{"n": 10, "s": 3, "r": 10}, {"n": 23, "s": 3, "m": 2}]},
                {"d": 5, "t": 1, "e": [{"n": 15, "s": 3, "r": 8}, {"n": 24, "s": 3, "r": 12}]},
                {"d": 6, "t": 1, "e": [{"n": 21, "s": 3, "m": 3}, {"n": 22, "s": 3, "m": 2}]},
                {"d": 7, "t": 0, "e": []}
            ]
        }
        return json.dumps(example, ensure_ascii=False)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        example = {"j": [{"d": 1, "t": 1, "e": [{"n": 1, "s": 3, "r": 12}]}]}
        return json.dumps(example, ensure_ascii=False)

    if client is None:
        return json.dumps({"j": []}, ensure_ascii=False)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un coach sportif. Répondez UNIQUEMENT avec le JSON compressé demandé."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        workout = response.choices[0].message.content.strip()
        
        # Nettoyer la réponse au cas où il y aurait des balises de code
        if workout.startswith('```'):
            workout = workout.split('\n', 1)[1]
        if workout.endswith('```'):
            workout = workout.rsplit('\n', 1)[0]
        
        return workout

    except Exception as e:
        return f"Une erreur est survenue lors de la génération du programme d'entraînement: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/login')
def login():
    """Login page with Firebase authentication"""
    return render_template('login.html')

@app.route('/workout-plan')
def workout_plan():
    """Page showing the current user's workout plan"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['uid']
    current_plan = None
    
    # D'abord essayer de récupérer depuis la mémoire
    current_plan = user_workout_plans.get(user_id, None)
    
    # Si pas en mémoire et Firestore disponible, essayer de récupérer depuis Firestore
    if not current_plan and db:
        try:
            docs = list(db.collection('workoutPlans').where('uid', '==', user_id).limit(1).stream())
            if docs:
                doc_data = docs[0].to_dict()
                current_plan = doc_data.get('plan')
                # Sauvegarder aussi en mémoire pour les prochaines fois
                user_workout_plans[user_id] = current_plan
                print(f"✅ Plan récupéré depuis Firestore pour l'utilisateur {user_id}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération Firestore: {e}")
    
    print(f"Plan actuel pour {user_id}: {current_plan is not None}")
    
    return render_template('workout_plan.html', 
                         user=session['user'], 
                         workout_plan=current_plan)

@app.route('/about')
def about():
    return render_template('about.html', user=session.get('user'))

@app.route('/contact')
def contact():
    return render_template('contact.html', user=session.get('user'))

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', user=session.get('user'))

@app.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase ID token"""
    try:
        if not firebase_initialized:
            return jsonify({
                'error': 'Firebase not initialized. Please check your Firebase credentials.',
                'details': 'Missing environment variables for Firebase configuration'
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No token provided'}), 400
        
        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception as firebase_error:
            print(f"Firebase token verification error: {firebase_error}")
            return jsonify({
                'error': 'Token verification failed',
                'details': str(firebase_error)
            }), 401
        
        session['user'] = {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email', ''),
            'name': decoded_token.get('name', ''),
            'picture': decoded_token.get('picture', '')
        }
        
        print(f"✅ User authenticated successfully: {session['user']['email']}")
        return jsonify({'success': True, 'user': session['user']})
        
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return jsonify({
            'error': 'Token verification error',
            'details': str(e)
        }), 401

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    else:
        return jsonify({'authenticated': False})

@app.route('/generate', methods=['POST'])
def generate():
    # Vérifier que l'utilisateur est connecté
    if 'user' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json(force=True)
    height = data.get('height', '')
    weight = data.get('weight', '')
    age = data.get('age', '')
    gym = data.get('gym', False)
    equipment_list = data.get('equipmentList', [])
    difficulty = data.get('difficulty', 'intermediate')
    max_session_duration = data.get('maxSessionDuration', None)
    max_workout_days = data.get('maxWorkoutDays', None)

    if not isinstance(equipment_list, list):
        equipment_list = []
    equipment_list = [str(item) for item in equipment_list]

    # Convertir les valeurs numériques
    if max_session_duration:
        try:
            max_session_duration = int(max_session_duration)
        except (ValueError, TypeError):
            max_session_duration = None
    
    if max_workout_days:
        try:
            max_workout_days = int(max_workout_days)
        except (ValueError, TypeError):
            max_workout_days = None

    # Générer le plan compressé
    compressed_plan = generate_workout_plan(height, weight, age, gym, equipment_list, 
                                          difficulty, max_session_duration, max_workout_days)
    
    # Sauvegarder pour l'utilisateur connecté
    if 'user' in session:
        user_id = session['user']['uid']
        try:
            # Parser et décompresser pour la sauvegarde
            compressed_data = json.loads(compressed_plan)
            decompressed_plan = decompress_workout_plan(compressed_data)
            user_workout_plans[user_id] = decompressed_plan
            
            # Sauvegarder aussi dans Firestore si disponible
            if db:
                try:
                    docs = list(db.collection('workoutPlans').where('uid', '==', user_id).limit(1).stream())
                    if docs:
                        doc_id = docs[0].id
                        db.collection('workoutPlans').document(doc_id).update({'plan': decompressed_plan})
                    else:
                        db.collection('workoutPlans').add({'uid': user_id, 'plan': decompressed_plan})
                except Exception as firestore_error:
                    print(f"⚠️ Erreur Firestore: {firestore_error}")
                    
        except json.JSONDecodeError:
            print(f"⚠️ Plan généré n'est pas un JSON valide")
    
    # Retourner le plan décompressé pour l'affichage
    try:
        compressed_data = json.loads(compressed_plan)
        final_plan = decompress_workout_plan(compressed_data)
        return jsonify({
            'plan': json.dumps(final_plan, ensure_ascii=False),
            'products': PRODUCT_SUGGESTIONS
        })
    except:
        return jsonify({
            'plan': compressed_plan,
            'products': PRODUCT_SUGGESTIONS
        })

@app.route('/save-plan', methods=['POST'])
def save_plan():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    plan = data.get('plan')
    user_id = session['user']['uid']
    
    if not plan:
        return jsonify({'error': 'No plan provided'}), 400
    
    try:
        # Sauvegarder en mémoire
        user_workout_plans[user_id] = plan
        
        # Sauvegarder dans Firestore si disponible
        if db:
            try:
                # Chercher le document existant
                docs = list(db.collection('workoutPlans').where('uid', '==', user_id).limit(1).stream())
                
                if docs:
                    # Mettre à jour le document existant
                    doc_id = docs[0].id
                    db.collection('workoutPlans').document(doc_id).update({'plan': plan})
                else:
                    # Créer un nouveau document
                    db.collection('workoutPlans').add({'uid': user_id, 'plan': plan})
                    
                print(f"✅ Plan sauvegardé dans Firestore pour l'utilisateur {user_id}")
            except Exception as firestore_error:
                print(f"⚠️ Erreur Firestore lors de la sauvegarde: {firestore_error}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-plan', methods=['POST'])
def update_plan():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    plan = data.get('plan')
    user_id = session['user']['uid']
    
    # Mettre à jour le plan en mémoire
    user_workout_plans[user_id] = plan
    
    # Si Firestore est disponible, sauvegarder aussi là-bas
    if db:
        try:
            # Chercher le document existant
            docs = db.collection('workoutPlans').where('uid', '==', user_id).limit(1).stream()
            doc_id = None
            for doc in docs:
                doc_id = doc.id
                break
            
            if doc_id:
                # Mettre à jour le document existant
                db.collection('workoutPlans').document(doc_id).update({'plan': plan})
            else:
                # Créer un nouveau document
                db.collection('workoutPlans').add({'uid': user_id, 'plan': plan})
        except Exception as e:
            print(f"Erreur Firestore: {e}")
    
    return jsonify({'success': True})

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

@app.route('/ads.txt')
def ads():
    return send_from_directory(app.static_folder, 'ads.txt')

@app.route('/legal')
def legal():
    return render_template('legal.html', user=session.get('user'))

@app.route('/terms')
def terms():
    return render_template('terms.html', user=session.get('user'))

@app.route('/blog')
def blog():
    return render_template('blog.html', user=session.get('user'), articles=BLOG_ARTICLES)

@app.route('/blog/<article_id>')
def article(article_id):
    article = get_article_by_id(article_id)
    if article:
        return render_template('article.html', user=session.get('user'), article=article, articles=BLOG_ARTICLES)
    else:
        return redirect(url_for('blog'))

if __name__ == '__main__':
    # Lance l'application Flask.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)