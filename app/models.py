from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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

# TODO: implement auctioning dates
class Artwork(models.Model):
	name = models.CharField(max_length=255)
	artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name="Artworks")
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="Artworks")
	publication_date = models.DateField()

	class Status(models.TextChoices):
		HIDDEN = "HI", _("Hidden")
		AUCTIONING = "AU", _("Auctioning")
		SOLD = "SO", _("Sold")

	status = models.CharField(
		max_length = 2,
		choices = Status,
		default = Status.HIDDEN,
	)

	def available(self):
		return self.status == self.Status.AUCTIONING
	
	def __str__(self):
		return f"Artwork {self.name} ({self.publication_date}), made by the artist: {self.artist}"


# TODO: manage sellers
class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to='img/', blank=True, null=True)
	class Meta:
		verbose_name_plural = "Customers"
	def __str__(self):
		return str(self.user)


