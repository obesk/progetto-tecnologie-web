from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import Artwork, Photo, Bid, Customer, Category, Artist
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
	filename = 	f"media/artwork_images/{f.name}"
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
	# def price(self):
	# 	highest_bid = self.object.Bids.aggregate(Max('amount', default=0))['amount__max']
	# 	return highest_bid
	def get_recommendations(self):
		artwork = self.object
		all_artworks = Artwork.objects.exclude(id=artwork.id)

		recommendations = []

		for other_artwork in all_artworks:
			score = 0

			# Similarity Score
			if other_artwork.seller == artwork.seller:
				score += 10  # Adjust weight as needed
			if other_artwork.category == artwork.category:
				score += 5  # Adjust weight as needed
			if other_artwork.artist == artwork.artist:
				score += 8  # Adjust weight as needed

			# Expiration Score
			time_to_expiry = other_artwork.auction_end - timezone.now()
			if time_to_expiry.total_seconds() > 0:
				score += max(0, (7 * 24 * 3600 - time_to_expiry.total_seconds()) / (7 * 24 * 3600)) * 10

			recommendations.append((other_artwork, score))

		recommendations.sort(key=lambda x: x[1], reverse=True)
		recommended_artworks = [rec[0] for rec in recommendations[:6]]

		return recommended_artworks

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['photos'] = self.object.Photos.all()
		context['recommended_artworks'] = self.get_recommendations()
		return context

@csrf_protect
def placeBid(request):
	if request.method == 'POST':
		user = request.user  # Retrieve the currently logged-in user
		customer = Customer.objects.get(user=user)
		artwork_id = request.POST.get('artwork_id')
		artwork = get_object_or_404(Artwork, id=artwork_id)
		try: 
			amount = float(request.POST.get('amount'))
			if amount > artwork.price():  # Replace `current_price` with the correct field name in your model
				Bid.objects.create(artwork=artwork, customer=customer, amount=amount)
				messages.success(request, 'Bid placed successfully!')
			else:
				messages.error(request, 'Bid amount must be higher than the current price.')
		except ValueError:
			messages.error(request, 'Invalid bid amount.')


		bid = Bid(artwork_id=artwork_id, customer=customer, amount=amount)
		bid.save()
		return redirect('app:artworkdetail', pk=artwork_id)  # Adjust 'app:artwork_detail' to your actual view name
	return redirect('app:artworkdetail')  # Fallback if not POST, adjust 'app:artwork_list' to your actual view name
	
def homepage(request):
    query = request.GET.get('q')
    category_filter = request.GET.get('category')
    artist_filter = request.GET.get('artist')

    latest_offers = Artwork.objects.filter(status=Artwork.Status.AUCTIONING).order_by('-publication_date')

    if query:
        latest_offers = latest_offers.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category_filter:
        latest_offers = latest_offers.filter(category_id=category_filter)
    
    if artist_filter:
        latest_offers = latest_offers.filter(artist_id=artist_filter)

    categories = Category.objects.all()
    artists = Artist.objects.all()

    context = {
        'latest_offers': latest_offers,
        'query': query,
        'categories': categories,
        'artists': artists,
        'category_filter': category_filter,
        'artist_filter': artist_filter,
    }
    return render(request, 'app/homepage.html', context)