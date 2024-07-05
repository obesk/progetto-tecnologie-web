from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Artwork, Artist, Category, AppUser
from django.utils import timezone
from datetime import timedelta
from django.http import Http404


class ArtworkDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_sold = User.objects.create_user(
            username="testusersold", password="12345"
        )
        self.app_user = AppUser.objects.create(user=self.user, is_seller=False)
        self.app_user_sold = AppUser.objects.create(
            user=self.user_sold, is_seller=False
        )
        self.artist = Artist.objects.create(
            name="Test", surname="Artist", biography="Bio", birthday="2000-01-01"
        )
        self.category = Category.objects.create(
            name="TestCategory", description="Description"
        )
        self.artwork = Artwork.objects.create(
            name="TestArtwork",
            artist=self.artist,
            category=self.category,
            publication_date=timezone.now().date(),
            auction_end=timezone.now() + timedelta(days=7),
            seller=self.app_user,
            status=Artwork.Status.AUCTIONING,
        )
        self.artwork_sold = Artwork.objects.create(
            name="TestArtworkSold",
            artist=self.artist,
            category=self.category,
            publication_date=timezone.now().date(),
            auction_end=timezone.now() - timedelta(days=7),
            seller=self.app_user,
            sold_to=self.app_user_sold,
            status=Artwork.Status.SOLD,
        )

    def test_access_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("app:artworkdetail", args=[self.artwork.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.artwork.name)
        self.assertContains(response, "Place Bid")
