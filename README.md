![image](https://img.shields.io/badge/Python-3.12-blue/?color=blue&logo=python&logoColor=9cf)
![image](https://img.shields.io/badge/FastAPI-0.109-%2344b78b/?color=%2344b78b&logo=fastapi&logoColor=2344b78b)

# Federation API

/!\ Ce projet est en cours de développement /!\

Ce projet vise à construire un framework fédératif pour les plateformes de données de santé.

Il est développé dans le contexte de l'Entrepôt de Données de Santé des Hôpitaux de Paris (AP-HP).

Ce framework fédératif peut être challengé et toute personne souhaitant contribuer peut le faire dans les issues de ce projet.

Ce framework fédératif vient avec une implémentation de référence sein de ce même projet Github.

## Description

Cas d'utilisation identifiés :

* La communication d'informations entre plateformes de données de santé. Ont été identifiés comme pertinents pour le moment les informations suivantes :
  * Un référentiel des plateformes connectées à cette instance 
  * Un référentiel des projet partagés entre les plateformes connectées et des détails à leur propos, par ex. leurs membres, le cadre réglementaire du projet, les entités liées à ce projet
  * Un référentiel des demandes d'export de jeux de données de plateforme à plateforme

Contraintes imposées : 

* La décentralisation : Une plateforme de données de santé peut se connecter à plusieurs instances de cette API de fédération pour échanger avec diverses plateformes de données de santé et limiter les informations partagées selon les besoins de chaque collaboration.
* Sécurité des informations échangées :
  * Cette API n'interagissant pas avec des données sensibles non chiffrées, elle peut être installée dans un endroit moins contraignant réglementairement (cloud non certifié HDS par ex.)
  * Toute information potentiellement sensible est chiffrée à l'aide d'un système similaire à mTLS : seules les plateformes clientes de cette API peuvent chiffrer et déchiffrer des informations sensibles contenues dans cette API. Cette API ne dispose d'aucune clé de chiffrement de la donnée stockée.
  * L'API est sécurisée au moyen d'un système d'authentification et chaque plateforme y accédant dispose de droits spécifiques
  * L'administrateur de l'API est le seul en capacité de délivrer à des plateformes des accès à cette API
  
# Stack technique

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com)
    - 🔍 [Pydantic](https://docs.pydantic.dev)
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org/)
    - 💾 [PostgreSQL](https://www.postgresql.org)
- 🔒 Secure password hashing
- 🔑 JWT authentication (for dev only)


# Setup

## 1. 🎨 Récupérer le projet
   ```sh
   git clone https://github.com/aphp/federation-api.git
   ```

## 2. 🚀 Lancer le projet

### Avec Docker 🐋
  ```sh
    cd federation-api
    docker compose --env-file .docker.env up
  ```

  * Accéder à la documentation de l'API sur [localhost:8000/docs](localhost:8000/docs)
  * S'authentifier avec **admin**/**1234** pour tester les routes de l'API


### Avec Uvicorn 🦄
Avec Python 3.12 déjà installé, procéder comme suit:  

  * Installer UV et créer un environnement virtuel

    ```sh
    cd federation-api
    pip install uv && uv venv py312venv && uv pip install --no-cache -r requirements.txt
    ```
  * Créer le fichier de variables d'environnement `federation-api/.env` à base du template `.env.example`

  * Démarrer Uvicorn
    ```sh
    source py312venv/bin/activate
    (py312venv) uvicorn platform_registry.main:app --port 8000 --reload
    ```
    
  * Accéder à la documentation de l'API sur [localhost:8000/docs](localhost:8000/docs)

  * Pour tester l'API:
    1. configurer un serveur de BD PotgreSQL et lancer les migrations avec `Alembic`
    ```sh
    (py312venv) alembic upgrade head
    ```
    2. Lancer le script pour créer un utilisateur initial `admin`
    ```sh
    (py312venv) python platform_registry/initial_data.py
    ```
    3. S'authentifier avec **admin**/**1234** pour tester les routes de l'API
