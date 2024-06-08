from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import Artwork, Photo
from .forms import ArtworkForm

import os

import logging

logger = logging.getLogger(__name__)

# Create your views here.

class ArtworksListView(ListView):
	title = "Artworks"
	model = Artwork
	template_name = "app/artwork_list.html"

# TODO: make name unique
def save_uploaded_file(f):
	filename = 	f"app/static/artwork_images/{f.name}"
	with open(filename, "wb+") as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return filename

class ArtworkCreateView(CreateView):
	form_class = ArtworkForm
	template_name = "app/create_artwork.html"
	success_url = reverse_lazy("app:artworklist")

	def form_valid(self, form):
		files = form.cleaned_data["images"]
		artwork = form.save()
		for f in files:
			filename = save_uploaded_file(f)
			photo = Photo(file=filename, artwork=artwork)
			photo.save()
		return super().form_valid(form)

class ArtworkDetailView(DetailView):
	model = Artwork 
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['photos'] = self.object.Photos.all()
		return context
