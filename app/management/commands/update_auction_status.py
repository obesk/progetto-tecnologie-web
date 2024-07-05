from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Artwork
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Command(BaseCommand):
    help = "Update auction status for artworks"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        artworks = Artwork.objects.filter(
            status=Artwork.Status.AUCTIONING, auction_end__lt=now
        )
        channel_layer = get_channel_layer()
        if channel_layer is None:
            self.stdout.write(
                self.style.ERROR("Channel layer is not configured properly")
            )

        for artwork in artworks:
            highest_bidder = artwork.Bids.order_by("-amount").first().customer
            self.stdout.write(
                self.style.SUCCESS(
                    f'Highest bidder for artwork "{artwork.name}" is {highest_bidder}'
                )
            )

            # FIXME: the notification is not working
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"artwork_{artwork.id}",
                    {
                        "type": "send_message",
                        "message": {
                            "title": "Sold Notification",
                            "body": f"The item {artwork.name} has been sold to {highest_bidder} for {artwork.price()}",
                        },
                    },
                )
            artwork.status = Artwork.Status.SOLD
            artwork.sold_to = highest_bidder
            artwork.save()
            self.stdout.write(
                self.style.SUCCESS(f'Artwork "{artwork.name}" marked as sold')
            )
