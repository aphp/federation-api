![image](https://img.shields.io/badge/Python-3.12-blue/?color=blue&logo=python&logoColor=9cf)
![image](https://img.shields.io/badge/FastAPI-0.109-%2344b78b/?color=%2344b78b&logo=fastapi&logoColor=2344b78b)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=aphp_federation-api&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=aphp_federation-api)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=aphp_federation-api&metric=coverage)](https://sonarcloud.io/summary/new_code?id=aphp_federation-api)

# Federation API

## Stack technique

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

  * Créer le fichier de variables d'environnement `federation-api/.env` à base du template `.env.example`

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
