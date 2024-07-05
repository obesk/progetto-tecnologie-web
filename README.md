# Progetto tecnologie web

## Descrizione
progetto per la gestione delle aste creato da Roberto Bertelli, matricola 146940

## Avvio del progetto

1. creare l'ambiente python e installare le dipendenze necessarie
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2. assicurarsi di aver installato redis

    ```bash
    sudo apt install redis=server
    ```

3. avviare il progetto

    ```bash
    python manage.py migrate
    python manage.py example_db
    python manage.py runserver
    ```

4. per testare la funzionalità di scadenza aste del progetto è anche necessario avviare celery beat e un worker

    ```bash
    ./start_celery
    ```

# Documentazione

La tesina del progetto si trova nella cartella `doc` 
