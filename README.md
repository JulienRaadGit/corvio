# Générateur de Programmes d'Entraînement

Un générateur de programmes d'entraînement personnalisés alimenté par l'IA, avec authentification Firebase et gestion des plans d'entraînement.

## 🚀 Fonctionnalités

- **Génération de programmes personnalisés** : Créez des programmes d'entraînement adaptés à vos besoins
- **Authentification Firebase** : Connectez-vous avec Google ou email/mot de passe pour sauvegarder vos plans
- **Plan d'entraînement 7 jours** : Visualisez votre programme complet avec jours de repos
- **Interface moderne** : Design responsive et intuitif
- **Sauvegarde automatique** : Vos plans sont automatiquement sauvegardés après connexion

## 📋 Prérequis

- Python 3.8+
- Projet Firebase (pour l'authentification)
- Clé API OpenAI (optionnel)

## 🛠️ Installation

1. **Cloner le repository**
   ```bash
   git clone <repository-url>
   cd corvio
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration des variables d'environnement**

   Créez un fichier `.env` à la racine du projet :
   ```env
   # Clé secrète Flask (changez cette valeur)
   SECRET_KEY=your-super-secret-key-change-this
   
   # Configuration Firebase (optionnel pour le développement)
   FIREBASE_PRIVATE_KEY_ID=your-firebase-private-key-id
   FIREBASE_PRIVATE_KEY=your-firebase-private-key
   FIREBASE_CLIENT_EMAIL=your-firebase-client-email
   FIREBASE_CLIENT_ID=your-firebase-client-id
   FIREBASE_CLIENT_CERT_URL=your-firebase-client-cert-url
   
   # Clé API OpenAI (optionnel)
   OPENAI_API_KEY=your-openai-api-key
   ```

## 🔐 Configuration Firebase

1. **Créer un projet Firebase**
   - Allez sur [Firebase Console](https://console.firebase.google.com/)
   - Créez un nouveau projet ou sélectionnez un projet existant

2. **Activer l'authentification**
   - Dans la console, allez dans "Authentication" > "Sign-in method"
   - Activez "Google" et "Email/Password"

3. **Configurer les domaines autorisés**
   - Dans "Authentication" > "Settings" > "Authorized domains"
   - Ajoutez vos domaines :
     - `localhost` (pour le développement)
     - `votre-domaine.com` (pour la production)

4. **Récupérer la configuration**
   - Dans "Project Settings" > "General"
   - Copiez la configuration Firebase
   - Pour la production, téléchargez la clé privée du service dans "Project Settings" > "Service accounts"

## 🚀 Lancement

1. **Mode développement**
   ```bash
   python app.py
   ```

2. **Mode production avec Gunicorn**
   ```bash
   gunicorn app:app
   ```

L'application sera accessible sur `http://localhost:5000`

## 📁 Structure du projet

```
corvio/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
├── static/
│   ├── css/
│   │   └── style.css     # Styles CSS
│   ├── js/
│   │   └── main.js       # JavaScript frontend
│   ├── data/
│   │   └── exercises.json # Liste des exercices
│   └── images/
│       └── placeholder.jpg # Image par défaut
└── templates/
    ├── index.html        # Page principale
    └── workout_plan.html # Page du plan d'entraînement
```

## 🎯 Utilisation

1. **Accès à l'application**
   - Ouvrez votre navigateur sur `http://localhost:5000`
   - Vous verrez la page d'accueil avec le formulaire de génération

2. **Connexion avec Google**
   - Cliquez sur "Se connecter avec Google" dans la barre de navigation
   - Autorisez l'application à accéder à votre compte Google
   - Vous serez redirigé vers la page d'accueil connecté

3. **Génération d'un programme**
   - Remplissez le formulaire avec vos informations
   - Sélectionnez votre équipement disponible
   - Cliquez sur "Générer le programme"
   - Votre plan sera automatiquement sauvegardé si vous êtes connecté

4. **Consultation de votre plan**
   - Cliquez sur "Mon Plan" dans la navigation
   - Visualisez votre programme de 7 jours
   - Imprimez votre plan si nécessaire

## 🔧 Configuration avancée

### Variables d'environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `SECRET_KEY` | Clé secrète Flask | Oui |
| `GOOGLE_CLIENT_ID` | ID client Google OAuth | Oui |
| `GOOGLE_CLIENT_SECRET` | Secret client Google OAuth | Oui |
| `OPENAI_API_KEY` | Clé API OpenAI | Non |

### Personnalisation

- **Exercices** : Modifiez `static/data/exercises.json` pour ajouter vos exercices
- **Images** : Ajoutez des images dans `static/images/exercises/`
- **Styles** : Personnalisez `static/css/style.css`
- **Logique** : Modifiez `static/js/main.js` pour le comportement frontend

## 🚀 Déploiement

### Heroku
1. Créez un compte Heroku
2. Installez Heroku CLI
3. Créez une nouvelle app :
   ```bash
   heroku create votre-app-name
   ```
4. Configurez les variables d'environnement :
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GOOGLE_CLIENT_ID=your-client-id
   heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret
   ```
5. Déployez :
   ```bash
   git push heroku main
   ```

### Autres plateformes
L'application est compatible avec toutes les plateformes supportant Python/Flask :
- PythonAnywhere
- DigitalOcean
- AWS
- Google Cloud Platform

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez que toutes les variables d'environnement sont configurées
2. Assurez-vous que les dépendances sont installées
3. Consultez les logs de l'application
4. Ouvrez une issue sur GitHub

## 🔮 Roadmap

- [ ] Base de données pour la persistance des données
- [ ] Historique des plans d'entraînement
- [ ] Suivi des progrès
- [ ] Notifications et rappels
- [ ] Mode sombre
- [ ] Application mobile