# redash_text_to_sql
# Overview
Repository for Text to SQL from Redash to BigQuery\
blog link: https://zenn.dev/hosimesi/articles/ab9e1cc3044a1b


# How to use
1. **Create a directory for persisting PostgreSQL data**
    Create a data directory for PostgreSQL to enable data persistence.
    ```bash
    $ mkdir postgress-data
    ```
2. **Initialize the database**
    Initialize the database used by Redash.
    ```bash
    docker compose run --rm server create_db
    ```
3. **Start the containers**
    Build and start Redash's various service containers using Docker Compose.
    ```bash
    docker compose up --build
    ```
