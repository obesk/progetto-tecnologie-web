from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth.models import User
from app.models import Artist, Category, AppUser, Artwork, Photo
import os
import shutil


class Command(BaseCommand):
    help = "Popola il database con dati di esempio"

    def handle(self, *args, **kwargs):
        call_command("flush", "--noinput")
        admin_user = User.objects.create_superuser(username="admin", password="admin")
        user1 = User.objects.create_user(username="seller1", password="password123")
        user2 = User.objects.create_user(username="buyer1", password="password123")
        user3 = User.objects.create_user(username="buyer2", password="password123")
        user4 = User.objects.create_user(username="seller2", password="password123")

        seller1 = AppUser.objects.create(user=user1, is_seller=True)
        buyer1 = AppUser.objects.create(user=user2, is_seller=False)
        buyer2 = AppUser.objects.create(user=user3, is_seller=False)
        seller2 = AppUser.objects.create(user=user4, is_seller=True)

        # Creazione artisti
        artist1 = Artist.objects.create(
            name="Leonardo",
            surname="Da Vinci",
            biography="Italian polymath of the Renaissance.",
            birthday="1452-04-15",
        )
        artist2 = Artist.objects.create(
            name="Vincent",
            surname="Van Gogh",
            biography="Dutch post-impressionist painter.",
            birthday="1853-03-30",
        )
        artist3 = Artist.objects.create(
            name="Unknown",
            surname="",
            biography="Ancient Greek sculptor.",
            birthday=None,
        )

        # Creazione categorie
        category1 = Category.objects.create(
            name="Painting", description="Artworks that involve painting."
        )
        category2 = Category.objects.create(
            name="Sculpture", description="Artworks that involve sculpture."
        )

        # Creazione opere d'arte
        artwork1 = Artwork.objects.create(
            name="Mona Lisa",
            artist=artist1,
            category=category1,
            publication_date=timezone.now().date(),
            auction_end=timezone.now() + timezone.timedelta(days=7),
            seller=seller1,
            description="A portrait of Lisa Gherardini, wife of Francesco del Giocondo.",
            status=Artwork.Status.AUCTIONING,
        )

        artwork2 = Artwork.objects.create(
            name="Starry Night",
            artist=artist2,
            category=category1,
            publication_date=timezone.now().date(),
            auction_end=timezone.now() + timezone.timedelta(days=7),
            seller=seller1,
            description="A depiction of the view from the east-facing window of his asylum room.",
            status=Artwork.Status.AUCTIONING,
        )

        artwork3 = Artwork.objects.create(
            name="Nike of Samotracia",
            artist=artist3,
            category=category2,
            publication_date=timezone.now().date(),
            auction_end=timezone.now() + timezone.timedelta(days=7),
            seller=seller2,
            description="An ancient Greek sculpture of Nike, the goddess of victory.",
            status=Artwork.Status.AUCTIONING,
        )

        # Spostamento delle immagini e creazione dei collegamenti con le opere d'arte
        sample_images_path = os.path.join("app", "sample_images")
        target_images_path = os.path.join("app", "static", "artwork_images")

        if not os.path.exists(target_images_path):
            os.makedirs(target_images_path)

        image_mapping = {
            "gioconda.jpeg": artwork1,
            "gioconda2.jpeg": artwork1,
            "starry1.jpg": artwork2,
            "starry2.jpg": artwork2,
            "nike.jpg": artwork3,
            "nike2.jpg": artwork3,
        }

        for image_name, artwork in image_mapping.items():
            src_path = os.path.join(sample_images_path, image_name)
            dst_path = os.path.join(target_images_path, image_name)
            shutil.copy(src_path, os.path.join("media", dst_path))

            photo = Photo.objects.create(file=dst_path, artwork=artwork)
            photo.save()

        self.stdout.write(self.style.SUCCESS("Database popolato con successo!"))
