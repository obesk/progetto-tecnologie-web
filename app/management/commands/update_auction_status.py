from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Artwork


class Command(BaseCommand):
    help = "Update auction status for artworks"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        artworks = Artwork.objects.filter(
            status=Artwork.Status.AUCTIONING, auction_end__lt=now
        )
        for artwork in artworks:
            artwork.status = Artwork.Status.SOLD
            artwork.save()
            self.stdout.write(
                self.style.SUCCESS(f'Artwork "{artwork.name}" marked as sold')
            )
