# Générateur de Programmes d'Entraînement

Un générateur de programmes d'entraînement personnalisés alimenté par l'IA, avec authentification Google et gestion des plans d'entraînement.

## 🚀 Fonctionnalités

- **Génération de programmes personnalisés** : Créez des programmes d'entraînement adaptés à vos besoins
- **Authentification Google** : Connectez-vous avec votre compte Google pour sauvegarder vos plans
- **Plan d'entraînement 7 jours** : Visualisez votre programme complet avec jours de repos
- **Interface moderne** : Design responsive et intuitif
- **Sauvegarde automatique** : Vos plans sont automatiquement sauvegardés après connexion

## 📋 Prérequis

- Python 3.8+
- Compte Google Cloud Platform (pour l'authentification)
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
   
   # Configuration Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   # Clé API OpenAI (optionnel)
   OPENAI_API_KEY=your-openai-api-key
   ```

## 🔐 Configuration Google OAuth

1. **Créer un projet Google Cloud Platform**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un nouveau projet ou sélectionnez un projet existant

2. **Activer l'API Google+**
   - Dans la console, allez dans "APIs & Services" > "Library"
   - Recherchez et activez "Google+ API"

3. **Créer des identifiants OAuth**
   - Allez dans "APIs & Services" > "Credentials"
   - Cliquez sur "Create Credentials" > "OAuth 2.0 Client IDs"
   - Sélectionnez "Web application"
   - Ajoutez les URIs de redirection autorisés :
     - `http://localhost:5000/callback` (pour le développement)
     - `https://votre-domaine.com/callback` (pour la production)

4. **Récupérer les identifiants**
   - Copiez le Client ID et Client Secret
   - Ajoutez-les dans votre fichier `.env`

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