from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import async_to_sync

from django.http import JsonResponse
from channels.layers import get_channel_layer



from .models import Artwork, Photo, Bid, Customer, Category, Artist
from .forms import ArtworkForm

import logging

logger = logging.getLogger(__name__)

class ArtworksListView(ListView):
	title = "Artworks"
	model = Artwork
	template_name = "app/artwork_list.html"
	def get_queryset(self):
		return Artwork.objects.filter(status=Artwork.Status.AUCTIONING)

class SellerProfile(ListView):
    model = Artwork
    template_name = "app/artwork_list.html"
    
    def get_queryset(self):
        self.seller = get_object_or_404(Customer, id=self.kwargs.get('seller_id'))
        return Artwork.objects.filter(seller=self.seller, status=Artwork.Status.AUCTIONING)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"{self.seller.user.username}'s Auctioning Artworks"
        context['seller_name'] = self.seller.user.username
        return context

def save_uploaded_file(f):
	filename = f"media/artwork_images/{f.name}"
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
	def get_recommendations(self):
		artwork = self.object
		all_artworks = Artwork.objects.exclude(id=artwork.id)

		recommendations = []

		for other_artwork in all_artworks:
			score = 0

			if other_artwork.seller == artwork.seller:
				score += 10
			if other_artwork.category == artwork.category:
				score += 5
			if other_artwork.artist == artwork.artist:
				score += 8

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
		user = request.user
		customer = Customer.objects.get(user=user)
		artwork_id = request.POST.get('artwork_id')
		artwork = get_object_or_404(Artwork, id=artwork_id)
		channel_layer = get_channel_layer()

		if channel_layer is None:
			return JsonResponse({'status': 'error', 'message': 'Channel layer is not configured correctly.'})

		try:
			amount = float(request.POST.get('amount'))
			if amount > artwork.price():
				previous_highest_bid = Bid.objects.filter(artwork=artwork).order_by('-amount').first()
				if previous_highest_bid and previous_highest_bid.customer != customer:
					async_to_sync(channel_layer.group_send)(
						f'artwork_{artwork_id}',
						{
							'type': 'send_message',
							'message': {
								'title': 'Outbid Notification',
								'body': f'You have been outbid on {artwork.name}'
							}
						}
					)

				Bid.objects.create(artwork=artwork, customer=customer, amount=amount)

				async_to_sync(channel_layer.group_send)(
					f'artwork_{artwork_id}',
					{
						'type': 'send_message',
						'message': {
							'title': 'New Bid Placed',
							'body': f'Your bid of {amount} on {artwork.name} has been placed successfully.'
						}
					}
				)
				return JsonResponse({'status': 'success'})
			else:
				return JsonResponse({'status': 'error', 'message': 'Bid amount must be higher than the current price.'})
		except ValueError:
			return JsonResponse({'status': 'error', 'message': 'Invalid bid amount.'})
	return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


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