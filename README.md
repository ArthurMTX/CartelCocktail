# Cartel Cocktails 🍸

Une application web qui recommande des cocktails basés sur l'analyse d'une playlist Spotify, avec une esthétique cartel.

## Fonctionnalités

1. **Analyse de Playlist Spotify**
   - Analyse les top 5 artistes d'une playlist
   - Détermine l'ambiance dominante basée sur les genres musicaux

2. **Recommandation de Cocktails**
   - Suggère des cocktails qui correspondent à l'ambiance de la playlist
   - Fournit des recettes détaillées avec ingrédients et instructions

3. **Interface Utilisateur Stylisée**
   - Design moderne avec une esthétique cartel
   - Affichage responsive des cocktails recommandés
   - Visualisation claire des résultats d'analyse

## Prérequis

- Python 3.11+
- Clés API:
  - Spotify API (Client ID & Secret)
  - CocktailDB API Key

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/ArthurMTX/CartelCocktail
cd cartel-cocktails
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement dans le .env
```bash
touch .env
SPOTIFY_CLIENT_ID='votre-client-id'
SPOTIFY_CLIENT_SECRET='votre-client-secret'
COCKTAILDB_API_KEY='votre-api-key'
```

## Tests

Exécuter les tests unitaires :
```bash
python -m pytest tests/
```

Les tests couvrent :
- Analyse de l'ambiance musicale
- Intégration avec l'API Spotify
- Recommandations de cocktails

## Lancement Local

1. Démarrer l'application :
```bash
python main.py
```

2. Accéder à l'application :
   - Ouvrir un navigateur
   - Aller sur `http://localhost:5000`
   - Entrer l'URL d'une playlist Spotify publique

## Structure du Projet

```
.
├── app.py              # Application Flask principale
├── spotify_client.py   # Client API Spotify
├── cocktail_client.py  # Client API CocktailDB
├── mood_analyzer.py    # Analyse d'ambiance musicale
├── templates/          # Templates HTML
├── static/            # Assets statiques (CSS, JS)
└── tests/             # Tests unitaires
```
