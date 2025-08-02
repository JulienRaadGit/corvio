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
        "date": "28 Juillet 2025",
        "image": "strength-training.png",
        "excerpt": "Découvrez les bases essentielles de la musculation : exercices fondamentaux, techniques correctes et progression adaptée aux débutants.",
        "content": """
        <h2>Les bases de la musculation</h2>
        <p>La musculation est une discipline sportive qui vise à développer la force et la masse musculaire. Pour les débutants, il est essentiel de comprendre les principes fondamentaux avant de commencer. Cette discipline ne se résume pas à soulever des poids, mais implique une approche holistique du développement physique.</p>
        
        <h3>Les exercices fondamentaux</h3>
        <p>Avant de vous lancer dans des exercices complexes, maîtrisez ces mouvements de base qui constituent la fondation de toute routine de musculation efficace :</p>
        <ul>
            <li><strong>Pompes</strong> : Excellent exercice pour les pectoraux et les triceps. Commencez par 3 séries de 5-10 répétitions selon votre niveau.</li>
            <li><strong>Squats</strong> : Indispensable pour les jambes et les fessiers. Cet exercice poly-articulaire engage tout le bas du corps.</li>
            <li><strong>Gainage</strong> : Pour renforcer la ceinture abdominale et améliorer votre posture générale.</li>
            <li><strong>Tractions</strong> : Développez votre dos et vos biceps avec cet exercice essentiel.</li>
            <li><strong>Fentes</strong> : Travaillez l'équilibre et renforcez vos jambes de manière unilatérale.</li>
        </ul>
        
        <h3>Techniques correctes</h3>
        <p>La qualité prime sur la quantité. Il est préférable de faire moins de répétitions avec une technique parfaite que l'inverse. Voici les points clés à respecter :</p>
        <ul>
            <li><strong>Contrôle du mouvement</strong> : Effectuez chaque répétition de manière contrôlée, sans à-coups.</li>
            <li><strong>Respiration</strong> : Expirez lors de l'effort, inspirez lors du retour à la position initiale.</li>
            <li><strong>Amplitude complète</strong> : Utilisez toute l'amplitude de mouvement pour maximiser l'efficacité.</li>
            <li><strong>Posture</strong> : Maintenez une posture correcte pour éviter les blessures.</li>
        </ul>
        
        <h3>Progression adaptée</h3>
        <p>Commencez progressivement et augmentez l'intensité au fil des semaines. Votre corps a besoin de temps pour s'adapter. Voici un plan de progression sur 8 semaines :</p>
        <ul>
            <li><strong>Semaines 1-2</strong> : Apprentissage des mouvements de base, 2-3 séances par semaine</li>
            <li><strong>Semaines 3-4</strong> : Augmentation du volume d'entraînement, ajout de variantes</li>
            <li><strong>Semaines 5-6</strong> : Intensification progressive, introduction de charges</li>
            <li><strong>Semaines 7-8</strong> : Optimisation de la routine, personnalisation selon vos objectifs</li>
        </ul>
        
        <h3>Récupération et nutrition</h3>
        <p>N'oubliez pas que la musculation ne se limite pas à l'entraînement. La récupération et la nutrition sont tout aussi importantes :</p>
        <ul>
            <li><strong>Sommeil</strong> : 7-9 heures par nuit pour une récupération optimale</li>
            <li><strong>Protéines</strong> : 1.6-2.2g par kg de poids corporel pour soutenir la croissance musculaire</li>
            <li><strong>Hydratation</strong> : Au moins 2 litres d'eau par jour</li>
            <li><strong>Étirements</strong> : 10-15 minutes après chaque séance</li>
        </ul>
        
        <h3>Objectifs et motivation</h3>
        <p>Définissez des objectifs réalistes et mesurables. Que ce soit perdre du poids, gagner en force ou améliorer votre silhouette, chaque objectif nécessite une approche spécifique. Gardez un journal d'entraînement pour suivre vos progrès et rester motivé.</p>
        """
    },
    {
        "id": "cardio-efficace",
        "title": "5 séances de cardio efficaces pour brûler les graisses",
        "category": "Cardio",
        "date": "30 Juillet 2025",
        "image": "cardio-workout.png",
        "excerpt": "Optimisez votre perte de poids avec ces entraînements cardio variés et intensifs, adaptés à tous les niveaux.",
        "content": """
        <h2>Le cardio pour perdre du poids</h2>
        <p>Le cardio est essentiel pour brûler des calories et améliorer votre condition cardiovasculaire. Contrairement aux idées reçues, il ne s'agit pas seulement de courir des heures sur un tapis. Voici 5 séances variées et efficaces pour maximiser vos résultats.</p>
        
        <h3>Séance 1 : HIIT (High Intensity Interval Training)</h3>
        <p>Le HIIT est l'une des méthodes les plus efficaces pour brûler des graisses. Cette technique alterne des périodes d'effort intense avec des périodes de récupération active.</p>
        <ul>
            <li><strong>Échauffement</strong> : 5 minutes de cardio léger</li>
            <li><strong>Intervalles</strong> : 30 secondes d'effort intense suivies de 30 secondes de récupération</li>
            <li><strong>Répétitions</strong> : 10-15 cycles selon votre niveau</li>
            <li><strong>Exercices</strong> : Burpees, jumping jacks, mountain climbers, high knees</li>
            <li><strong>Récupération</strong> : 5 minutes d'étirements</li>
        </ul>
        
        <h3>Séance 2 : Course à pied progressive</h3>
        <p>La course à pied reste un classique efficace. Cette séance progressive vous permettra d'améliorer votre endurance tout en brûlant des calories.</p>
        <ul>
            <li><strong>Échauffement</strong> : 10 minutes de marche rapide</li>
            <li><strong>Phase 1</strong> : 5 minutes de course à un rythme modéré</li>
            <li><strong>Phase 2</strong> : 10 minutes d'alternance course/marche</li>
            <li><strong>Phase 3</strong> : 5 minutes de course continue</li>
            <li><strong>Récupération</strong> : 5 minutes de marche lente</li>
        </ul>
        
        <h3>Séance 3 : Vélo avec variations d'intensité</h3>
        <p>Le vélo est excellent pour les articulations tout en offrant un entraînement cardio efficace. Cette séance combine endurance et intensité.</p>
        <ul>
            <li><strong>Échauffement</strong> : 10 minutes à résistance faible</li>
            <li><strong>Intervalles</strong> : 2 minutes à haute intensité, 3 minutes à intensité modérée</li>
            <li><strong>Durée totale</strong> : 45 minutes</li>
            <li><strong>Variations</strong> : Montez en selle, sprints assis, pédalage en danseuse</li>
        </ul>
        
        <h3>Séance 4 : Natation complète</h3>
        <p>La natation est un sport complet qui sollicite tous les muscles tout en préservant les articulations. Parfait pour la récupération active.</p>
        <ul>
            <li><strong>Échauffement</strong> : 5 minutes de nage libre à rythme lent</li>
            <li><strong>Techniques</strong> : Alternance crawl, brasse, dos crawlé</li>
            <li><strong>Intervalles</strong> : 50m sprint, 50m récupération</li>
            <li><strong>Durée</strong> : 30-45 minutes selon votre niveau</li>
        </ul>
        
        <h3>Séance 5 : Marche rapide en extérieur</h3>
        <p>Accessible à tous, la marche rapide peut être très efficace si pratiquée correctement. Idéale pour les débutants ou en récupération.</p>
        <ul>
            <li><strong>Intensité</strong> : Rythme soutenu (vous devez pouvoir parler mais pas chanter)</li>
            <li><strong>Durée</strong> : 45-60 minutes</li>
            <li><strong>Variations</strong> : Inclinaisons, escaliers, terrains variés</li>
            <li><strong>Bonus</strong> : Exposition à la nature et vitamine D</li>
        </ul>
        
        <h3>Optimisation de vos séances cardio</h3>
        <p>Pour maximiser l'efficacité de vos entraînements cardio :</p>
        <ul>
            <li><strong>Fréquence</strong> : 3-5 séances par semaine selon vos objectifs</li>
            <li><strong>Intensité</strong> : Variez entre séances d'endurance et d'intensité</li>
            <li><strong>Progression</strong> : Augmentez progressivement la durée et l'intensité</li>
            <li><strong>Récupération</strong> : Accordez-vous au moins un jour de repos par semaine</li>
            <li><strong>Hydratation</strong> : Buvez avant, pendant et après l'effort</li>
        </ul>
        
        <h3>Mesure de vos progrès</h3>
        <p>Suivez vos améliorations pour rester motivé :</p>
        <ul>
            <li><strong>Fréquence cardiaque</strong> : Mesurez votre FC de repos et d'effort</li>
            <li><strong>Durée</strong> : Augmentez progressivement la durée de vos séances</li>
            <li><strong>Intensité</strong> : Notez vos sensations d'effort (échelle de Borg)</li>
            <li><strong>Récupération</strong> : Observez l'amélioration de votre temps de récupération</li>
        </ul>
        """
    },
    {
        "id": "nutrition-sportive",
        "title": "Nutrition sportive : que manger avant et après l'entraînement",
        "category": "Nutrition",
        "date": "31 Juillet 2025",
        "image": "nutrition.png",
        "excerpt": "Maximisez vos performances et votre récupération grâce à une alimentation adaptée à vos objectifs sportifs.",
        "content": """
        <h2>L'importance de la nutrition sportive</h2>
        <p>Une alimentation adaptée peut faire la différence entre une séance moyenne et une séance exceptionnelle. La nutrition sportive ne se limite pas à manger plus, mais à manger mieux au bon moment. Voici un guide complet pour optimiser vos performances.</p>
        
        <h3>Avant l'entraînement : Le carburant</h3>
        <p>Ce que vous mangez avant l'effort détermine vos performances. Voici un timing précis pour optimiser votre énergie :</p>
        <ul>
            <li><strong>2-3 heures avant</strong> : Repas complet avec glucides complexes (riz, pâtes, quinoa), protéines maigres (poulet, poisson, œufs) et légumes. Exemple : Riz complet + poulet + brocolis</li>
            <li><strong>1 heure avant</strong> : Collation légère riche en glucides simples (banane, pomme, barre énergétique naturelle)</li>
            <li><strong>30 minutes avant</strong> : Hydratation suffisante (500ml d'eau) et éventuellement un café pour booster les performances</li>
            <li><strong>15 minutes avant</strong> : Évitez de manger pour laisser le sang disponible pour les muscles</li>
        </ul>
        
        <h3>Pendant l'entraînement : L'hydratation</h3>
        <p>Pour les séances de moins d'une heure, l'eau suffit. Pour les efforts plus longs :</p>
        <ul>
            <li><strong>Hydratation</strong> : 150-200ml toutes les 15-20 minutes</li>
            <li><strong>Électrolytes</strong> : Pour les efforts de plus d'une heure, ajoutez du sel ou une boisson isotonique</li>
            <li><strong>Glucides</strong> : Pour les séances de plus de 90 minutes, consommez 30-60g de glucides par heure</li>
        </ul>
        
        <h3>Après l'entraînement : La fenêtre anabolique</h3>
        <p>Les 30 premières minutes après l'effort sont cruciales pour la récupération et la croissance musculaire :</p>
        <ul>
            <li><strong>Dans les 30 minutes</strong> : Protéines (20-30g) + glucides simples (30-60g). Exemple : Shake protéiné + banane ou yaourt grec + miel</li>
            <li><strong>Dans les 2 heures</strong> : Repas équilibré complet avec protéines, glucides complexes et lipides</li>
            <li><strong>Hydratation</strong> : Compensez les pertes hydriques (1.5L par kg perdu)</li>
        </ul>
        
        <h3>Macronutriments selon vos objectifs</h3>
        <p>Adaptez vos apports selon vos objectifs sportifs :</p>
        <ul>
            <li><strong>Perte de poids</strong> : Déficit calorique modéré (-300 à -500 kcal), protéines élevées (1.8-2.2g/kg), glucides modérés</li>
            <li><strong>Prise de muscle</strong> : Surplus calorique léger (+200 à +500 kcal), protéines élevées (1.6-2.2g/kg), glucides suffisants</li>
            <li><strong>Endurance</strong> : Glucides élevés (6-10g/kg), protéines modérées (1.2-1.6g/kg)</li>
            <li><strong>Force</strong> : Protéines élevées (1.6-2.2g/kg), glucides modérés, lipides suffisants</li>
        </ul>
        
        <h3>Micronutriments essentiels</h3>
        <p>N'oubliez pas les vitamines et minéraux qui soutiennent vos performances :</p>
        <ul>
            <li><strong>Vitamine D</strong> : Essentielle pour la force musculaire et la récupération</li>
            <li><strong>Magnésium</strong> : Aide à la contraction musculaire et prévient les crampes</li>
            <li><strong>Zinc</strong> : Important pour la synthèse protéique et la récupération</li>
            <li><strong>Vitamines B</strong> : Nécessaires pour la production d'énergie</li>
            <li><strong>Antioxydants</strong> : Vitamines C et E pour lutter contre le stress oxydatif</li>
        </ul>
        
        <h3>Supplémentation intelligente</h3>
        <p>Certains suppléments peuvent compléter une alimentation équilibrée :</p>
        <ul>
            <li><strong>Protéines en poudre</strong> : Pratique pour atteindre vos besoins quotidiens</li>
            <li><strong>Créatine</strong> : Améliore les performances en force et puissance</li>
            <li><strong>BCAA</strong> : Peuvent aider à la récupération musculaire</li>
            <li><strong>Oméga-3</strong> : Anti-inflammatoires naturels</li>
            <li><strong>Vitamine D</strong> : Complément souvent nécessaire en hiver</li>
        </ul>
        
        <h3>Planification et préparation</h3>
        <p>La réussite en nutrition sportive passe par une bonne organisation :</p>
        <ul>
            <li><strong>Planification hebdomadaire</strong> : Préparez vos repas à l'avance</li>
            <li><strong>Liste de courses</strong> : Établissez une liste basée sur vos besoins nutritionnels</li>
            <li><strong>Préparation</strong> : Cuisinez en batch pour gagner du temps</li>
            <li><strong>Flexibilité</strong> : Adaptez selon vos séances du jour</li>
        </ul>
        """
    },
    {
        "id": "entrainement-domicile",
        "title": "Programme d'entraînement complet à domicile sans matériel",
        "category": "Entraînement",
        "date": "1 Août 2025",
        "image": "home-workout.png",
        "excerpt": "Restez en forme même sans salle de sport avec ce programme complet utilisant uniquement votre poids de corps.",
        "content": """
        <h2>L'entraînement à domicile</h2>
        <p>Pas besoin d'équipement coûteux pour se muscler et rester en forme. Votre corps est votre meilleur outil. L'entraînement à domicile offre de nombreux avantages : flexibilité horaire, économies, pas de déplacement, et la possibilité de s'entraîner n'importe où. Voici un programme complet et progressif.</p>
        
        <h3>Programme hebdomadaire complet</h3>
        <p>Ce programme de 7 jours est conçu pour solliciter tous les groupes musculaires tout en respectant les principes de récupération :</p>
        <ul>
            <li><strong>Lundi - Haut du corps</strong> : Pompes, dips, gainage, tractions (si possible)</li>
            <li><strong>Mardi - Bas du corps</strong> : Squats, fentes, mollets, wall sit</li>
            <li><strong>Mercredi - Repos actif</strong> : Étirements, yoga, marche</li>
            <li><strong>Jeudi - Cardio HIIT</strong> : Burpees, jumping jacks, mountain climbers</li>
            <li><strong>Vendredi - Corps complet</strong> : Circuit training avec tous les exercices</li>
            <li><strong>Samedi - Flexibilité</strong> : Étirements, yoga, mobilité</li>
            <li><strong>Dimanche - Repos complet</strong> : Récupération, promenade légère</li>
        </ul>
        
        <h3>Exercices clés par groupe musculaire</h3>
        <p>Maîtrisez ces exercices fondamentaux avant d'ajouter de la complexité :</p>
        
        <h4>Haut du corps</h4>
        <ul>
            <li><strong>Pompes classiques</strong> : 3 séries de 8-15 répétitions</li>
            <li><strong>Pompes diamant</strong> : Pour les triceps (plus difficile)</li>
            <li><strong>Pompes larges</strong> : Pour les pectoraux</li>
            <li><strong>Dips sur chaise</strong> : Triceps et épaules</li>
            <li><strong>Gainage planche</strong> : 3 séries de 30-60 secondes</li>
        </ul>
        
        <h4>Bas du corps</h4>
        <ul>
            <li><strong>Squats</strong> : 3 séries de 15-20 répétitions</li>
            <li><strong>Fentes avant</strong> : 3 séries de 10 par jambe</li>
            <li><strong>Fentes latérales</strong> : Pour les adducteurs</li>
            <li><strong>Wall sit</strong> : 3 séries de 30-60 secondes</li>
            <li><strong>Mollets</strong> : 3 séries de 20-30 répétitions</li>
        </ul>
        
        <h4>Cardio et explosivité</h4>
        <ul>
            <li><strong>Burpees</strong> : Exercice complet par excellence</li>
            <li><strong>Jumping jacks</strong> : Cardio simple et efficace</li>
            <li><strong>Mountain climbers</strong> : Cardio + gainage</li>
            <li><strong>High knees</strong> : Cardio intense</li>
            <li><strong>Jump squats</strong> : Force explosive</li>
        </ul>
        
        <h3>Progression sur 12 semaines</h3>
        <p>Ce plan de progression vous permettra d'évoluer de débutant à intermédiaire :</p>
        
        <h4>Semaines 1-4 : Fondation</h4>
        <ul>
            <li>Apprentissage des mouvements de base</li>
            <li>2-3 séances par semaine</li>
            <li>Focus sur la technique</li>
            <li>Récupération suffisante</li>
        </ul>
        
        <h4>Semaines 5-8 : Développement</h4>
        <ul>
            <li>Augmentation du volume</li>
            <li>Ajout de variantes</li>
            <li>4-5 séances par semaine</li>
            <li>Introduction de circuits</li>
        </ul>
        
        <h4>Semaines 9-12 : Intensification</h4>
        <ul>
            <li>Complexité accrue</li>
            <li>Supersets et circuits</li>
            <li>5-6 séances par semaine</li>
            <li>Objectifs personnalisés</li>
        </ul>
        
        <h3>Variantes et progressions</h3>
        <p>Une fois les exercices de base maîtrisés, ajoutez de la difficulté :</p>
        <ul>
            <li><strong>Pompes</strong> : Pompes déclinées, pompes sur une main</li>
            <li><strong>Squats</strong> : Squats sautés, pistol squats</li>
            <li><strong>Gainage</strong> : Planche latérale, gainage dynamique</li>
            <li><strong>Cardio</strong> : Burpees avec pompe, mountain climbers croisés</li>
        </ul>
        
        <h3>Équipement minimal (optionnel)</h3>
        <p>Si vous souhaitez investir dans du matériel basique :</p>
        <ul>
            <li><strong>Tapis de yoga</strong> : Confort et amorti</li>
            <li><strong>Élastiques</strong> : Résistance progressive</li>
            <li><strong>Haltères</strong> : Pour ajouter de la charge</li>
            <li><strong>Barre de traction</strong> : Pour les tractions</li>
        </ul>
        
        <h3>Motivation et suivi</h3>
        <p>Gardez la motivation avec ces stratégies :</p>
        <ul>
            <li><strong>Journal d'entraînement</strong> : Notez vos progrès</li>
            <li><strong>Photos</strong> : Suivez vos transformations</li>
            <li><strong>Objectifs SMART</strong> : Spécifiques, mesurables, atteignables</li>
            <li><strong>Communauté</strong> : Rejoignez des groupes en ligne</li>
            <li><strong>Variété</strong> : Changez régulièrement vos routines</li>
        </ul>
        """
    },
    {
        "id": "recuperation-musculaire",
        "title": "Les secrets d'une récupération musculaire optimale",
        "category": "Récupération",
        "date": "2 Août 2025",
        "image": "recovery.png",
        "excerpt": "Découvrez les techniques et astuces pour accélérer votre récupération et éviter les blessures.",
        "content": """
        <h2>La récupération : clé du progrès</h2>
        <p>La récupération est aussi importante que l'entraînement lui-même. C'est pendant cette phase que vos muscles se reconstruisent, s'adaptent et se renforcent. Une récupération optimale vous permettra de progresser plus rapidement tout en évitant les blessures et le surentraînement.</p>
        
        <h3>Comprendre le processus de récupération</h3>
        <p>Après un entraînement, votre corps passe par plusieurs phases de récupération :</p>
        <ul>
            <li><strong>Phase immédiate (0-4h)</strong> : Restauration des réserves énergétiques, réduction de l'inflammation</li>
            <li><strong>Phase courte (4-24h)</strong> : Réparation des micro-lésions musculaires, synthèse protéique</li>
            <li><strong>Phase longue (24-72h)</strong> : Adaptation musculaire, amélioration de la performance</li>
            <li><strong>Phase de surcompensation</strong> : Le corps se renforce au-delà du niveau initial</li>
        </ul>
        
        <h3>Techniques de récupération actives</h3>
        <p>La récupération active favorise la circulation sanguine et accélère l'élimination des déchets métaboliques :</p>
        <ul>
            <li><strong>Étirements dynamiques</strong> : Après chaque séance, 10-15 minutes d'étirements progressifs</li>
            <li><strong>Récupération active</strong> : 20-30 minutes de cardio léger (marche, vélo) le lendemain d'une séance intense</li>
            <li><strong>Mobilité articulaire</strong> : Exercices de mobilité pour maintenir l'amplitude de mouvement</li>
            <li><strong>Yoga ou pilates</strong> : Améliore la flexibilité et réduit le stress</li>
        </ul>
        
        <h3>Techniques de récupération passives</h3>
        <p>Ces techniques favorisent la relaxation et la régénération :</p>
        <ul>
            <li><strong>Sommeil</strong> : 7-9 heures par nuit, qualité plus importante que quantité</li>
            <li><strong>Étirements statiques</strong> : 30 secondes par muscle, sans forcer</li>
            <li><strong>Massage</strong> : Auto-massage avec rouleau de mousse ou balle de tennis</li>
            <li><strong>Compression</strong> : Vêtements compressifs pour améliorer la circulation</li>
            <li><strong>Contraste chaud/froid</strong> : Douche alternée ou bain de glace</li>
        </ul>
        
        <h3>Nutrition pour la récupération</h3>
        <p>L'alimentation joue un rôle crucial dans la récupération musculaire :</p>
        <ul>
            <li><strong>Protéines</strong> : 20-30g dans les 30 minutes post-entraînement pour la synthèse musculaire</li>
            <li><strong>Glucides</strong> : 30-60g pour restaurer les réserves de glycogène</li>
            <li><strong>Antioxydants</strong> : Fruits et légumes colorés pour lutter contre le stress oxydatif</li>
            <li><strong>Oméga-3</strong> : Anti-inflammatoires naturels (poissons gras, noix)</li>
            <li><strong>Hydratation</strong> : Compensez les pertes hydriques (1.5L par kg perdu)</li>
        </ul>
        
        <h3>Gestion du stress et récupération mentale</h3>
        <p>Le stress chronique peut impacter négativement votre récupération :</p>
        <ul>
            <li><strong>Techniques de respiration</strong> : Respiration diaphragmatique pour réduire le cortisol</li>
            <li><strong>Méditation</strong> : 10-15 minutes par jour pour la relaxation mentale</li>
            <li><strong>Nature</strong> : Marche en extérieur pour réduire le stress</li>
            <li><strong>Sommeil de qualité</strong> : Chambre fraîche, sombre et silencieuse</li>
            <li><strong>Déconnexion</strong> : Limitez les écrans avant le coucher</li>
        </ul>
        
        <h3>Signes de surentraînement à surveiller</h3>
        <p>Reconnaissez ces signaux pour éviter le surentraînement :</p>
        <ul>
            <li><strong>Physiques</strong> : Fatigue persistante, baisse de performance, douleurs articulaires</li>
            <li><strong>Mentaux</strong> : Irritabilité, troubles du sommeil, perte de motivation</li>
            <li><strong>Immunitaires</strong> : Infections fréquentes, temps de récupération prolongé</li>
            <li><strong>Cardiovasculaires</strong> : Fréquence cardiaque de repos élevée</li>
        </ul>
        
        <h3>Planification de la récupération</h3>
        <p>Intégrez la récupération dans votre planification d'entraînement :</p>
        <ul>
            <li><strong>Déload week</strong> : Une semaine de réduction d'intensité toutes les 4-6 semaines</li>
            <li><strong>Récupération active</strong> : 1-2 jours par semaine</li>
            <li><strong>Sommeil prioritaire</strong> : Planifiez vos heures de coucher</li>
            <li><strong>Évaluation régulière</strong> : Notez votre niveau de fatigue et d'énergie</li>
            <li><strong>Adaptation</strong> : Ajustez selon vos sensations et votre récupération</li>
        </ul>
        
        <h3>Outils et technologies de récupération</h3>
        <p>Utilisez ces outils pour optimiser votre récupération :</p>
        <ul>
            <li><strong>Rouleau de mousse</strong> : Auto-massage et relâchement myofascial</li>
            <li><strong>Balle de tennis/lacrosse</strong> : Massage ciblé des points de tension</li>
            <li><strong>Vêtements compressifs</strong> : Améliorent la circulation et réduisent les courbatures</li>
            <li><strong>Appareils de récupération</strong> : Pistolets de massage, appareils de stimulation électrique</li>
            <li><strong>Applications de suivi</strong> : Monitoring du sommeil, de la fréquence cardiaque</li>
        </ul>
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

@app.route('/robots.txt')
def robots():
    """Sert le fichier robots.txt"""
    return send_from_directory(app.static_folder, 'robots.txt')

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

@app.route('/sitemap.xml')
def sitemap():
    """Génère un sitemap XML pour le SEO"""
    from flask import make_response
    from datetime import datetime
    
    # Liste des URLs du site
    urls = [
        {'loc': url_for('index', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '1.0'},
        {'loc': url_for('about', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.8'},
        {'loc': url_for('contact', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.7'},
        {'loc': url_for('blog', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.8'},
        {'loc': url_for('privacy', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.5'},
        {'loc': url_for('terms', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.5'},
        {'loc': url_for('legal', _external=True), 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.5'},
    ]
    
    # Générer le XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml'
    return response

if __name__ == '__main__':
    # Lance l'application Flask.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)