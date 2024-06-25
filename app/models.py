from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Max
from django.utils import timezone
from datetime import timedelta
import os


class Artist(models.Model):
	name = models.CharField(max_length=120)
	surname = models.CharField(max_length=120)
	biography = models.TextField()
	birthday = models.DateField()
	def __str__(self):
		return f"{self.name} {self.surname}, born in {self.birthday}"

class Category(models.Model):
	name = models.CharField(max_length=120)
	description = models.TextField(max_length=120)
	class Meta:
		verbose_name_plural = "Categories"

	def __str__(self):
		return str(self.name)

class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to='img/', blank=True, null=True)
	is_seller = models.BooleanField(default=False)
	class Meta:
		verbose_name_plural = "Customers"
	def __str__(self):
		return str(self.user)
	notify_outbid = models.BooleanField(default=True)
	notify_auction_end = models.BooleanField(default=True)

class Artwork(models.Model):
	name = models.CharField(max_length=255)
	artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name="Artworks")
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="Artworks")
	publication_date = models.DateField()
	auction_end = models.DateTimeField(default=timezone.now() + timedelta(days=7))
	seller = models.ForeignKey(Customer, on_delete=models.CASCADE, limit_choices_to={'is_seller': True}, null=True)

	description = models.TextField(max_length=255, default="")

	class Status(models.TextChoices):
		HIDDEN = "HI", _("Hidden")
		AUCTIONING = "AU", _("Auctioning")
		SOLD = "SO", _("Sold")

	status = models.CharField(
		max_length = 2,
		choices = Status.choices,
		default = Status.HIDDEN,
	)

	def available(self):
		return self.status == self.Status.AUCTIONING

	def price(self):
		highest_bid = self.Bids.aggregate(Max('amount', default=0))['amount__max']
		return highest_bid or 0
	
	def __str__(self):
		return f"Artwork {self.name} ({self.publication_date}), made by the artist: {self.artist}"



class Bid(models.Model):
	artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name="Bids")
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="Bids")
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	class Meta:
		verbose_name_plural = "Bids"
	def __str__(self):
		return f"{self.customer} bid {self.amount} euros, for artwork: {self.artwork}"

	
	
class Photo(models.Model): 
	file = models.ImageField('Attachment', upload_to="app/static/artwork_images")
	upload_date = models.DateTimeField(auto_now_add=True)
	artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name="Photos")

	def get_static_path(self):
		return os.path.join("/static/artwork_images/", os.path.basename(self.file.name))

