celery -A auctions beat --loglevel=info &
celery -A auctions worker --loglevel=info &