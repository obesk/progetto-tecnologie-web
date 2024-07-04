from celery import shared_task
from django.core.management import call_command


@shared_task
def update_auction_status():
    call_command("update_auction_status")
