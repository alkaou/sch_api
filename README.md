# API School Manager

API avancée pour la gestion de données scolaires avec un module de chat IA (Google Gemini).

## Structure du projet

(à compléter)

## Pré-requis

- Python 3.9+
- Pip
- Vercel CLI

## Installation locale

1.  Clonez le dépôt.
2.  Créez un environnement virtuel :
    ```bash
    python -m venv venv
    ```
3.  Activez l'environnement :
    -   Windows: `venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`
4.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
5.  Créez un fichier `.env` à la racine et ajoutez les variables d'environnement nécessaires.

## Variables d'environnement

Créez un fichier `.env` et ajoutez les clés suivantes :

```
# Clé API pour Google Gemini
GOOGLE_API_KEY="VOTRE_CLE_API_GOOGLE"

```

### `POST /config`

Met à jour la configuration globale de l'API. Les changements sont temporaires (en mémoire).

**Corps de la requête :**
```json
{
  "GEMINI_DEFAULT_MODEL": "gemini-pro",
  "GEMINI_DEFAULT_TEMPERATURE": 0.9
}
```

### `GET /config`

Récupère la configuration actuelle de l'application.

## Lancer les tests

Assurez-vous d'avoir installé `pytest` (inclus dans `requirements.txt`).

```bash
pytest
```

## Utilisation avec Postman / Insomnia

Une collection Postman (`api-school-manager.postman_collection.json`) a été mise à jour pour refléter la nouvelle logique de l'API.

1.  Importez le fichier `api-school-manager.postman_collection.json` dans votre client API.
2.  La collection utilise une variable `{{baseUrl}}`. Par défaut, elle est définie sur `http://127.0.0.1:5000` pour les tests locaux. Vous pouvez la modifier pour pointer vers votre URL de production Vercel.
3.  Le endpoint `/chat` s'utilise maintenant avec `form-data`. Vous pouvez y attacher un fichier directement.

## Lancer l'API localement

```bash
$env:FLASK_APP = "api.index:create_app"
$env:FLASK_ENV = "development"
flask run
```

L'API sera disponible à l'adresse `http://127.0.0.1:5000`.

## Déploiement sur Vercel

1.  Connectez-vous à Vercel :
    ```bash
    vercel login
    ```
2.  Déployez le projet :
    ```bash
    vercel --prod
    ```
