from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Artwork, Artist, Category, AppUser, Bid
from django.utils import timezone
from datetime import timedelta


class PlaceBidTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.seller = User.objects.create_user(username="seller", password="12345")
        self.app_user = AppUser.objects.create(user=self.user, is_seller=False)
        self.app_seller = AppUser.objects.create(user=self.seller, is_seller=True)
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
            seller=self.app_seller,
            status=Artwork.Status.AUCTIONING,
        )

    def test_valid_bid(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("app:placebid"),
            {"artwork_id": self.artwork.id, "amount": 100},
            follow=True,
        )
        self.assertRedirects(
            response, reverse("app:artworkdetail", kwargs={"pk": self.artwork.id})
        )
        self.assertEqual(Bid.objects.count(), 1)
        self.assertEqual(Bid.objects.first().amount, 100)

    def test_invalid_bid_amount(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("app:placebid"),
            {"artwork_id": self.artwork.id, "amount": "invalid"},
            follow=True,
        )
        self.assertRedirects(
            response, reverse("app:artworkdetail", kwargs={"pk": self.artwork.id})
        )
        self.assertContains(response, "Invalid bid amount.")
        self.assertEqual(Bid.objects.count(), 0)

    def test_bid_less_than_current_price(self):
        Bid.objects.create(artwork=self.artwork, customer=self.app_user, amount=100)
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("app:placebid"),
            {"artwork_id": self.artwork.id, "amount": 50},
            follow=True,
        )
        self.assertRedirects(
            response, reverse("app:artworkdetail", kwargs={"pk": self.artwork.id})
        )
        self.assertContains(
            response, "Bid amount must be higher than the current price."
        )
        self.assertEqual(Bid.objects.count(), 1)
