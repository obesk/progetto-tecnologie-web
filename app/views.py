from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Artwork

# Create your views here.

class ArtworksListView(ListView):
	title = "Artworks"
	model = Artwork
	template_name = "app/artwork_list.html"