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

from .models import Artwork, Photo, Bid, Customer
from .forms import ArtworkForm, CancelAuctionForm
from .mixins import ArtworkFilterMixin

import logging

logger = logging.getLogger(__name__)

class HomePageView(ArtworkFilterMixin, ListView):
	model = Artwork
	template_name = 'app/homepage.html'
	context_object_name = 'latest_offers'
	queryset = Artwork.objects.filter(status=Artwork.Status.AUCTIONING)

class SellerProfile(ArtworkFilterMixin, ListView):
	model = Artwork
	template_name = "app/seller_auctioning_artworks_list.html"
	
	def get_queryset(self):
		self.seller = get_object_or_404(Customer, id=self.kwargs.get('seller_id'))
		queryset = super().get_queryset()
		return queryset.filter(seller=self.seller, status=Artwork.Status.AUCTIONING)
	
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
		context['seller'] = self.object.seller
		return context

class SellerArtworkDetailView(DetailView):
	model = Artwork
	template_name = "app/artwork_manage.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['photos'] = self.object.Photos.all()
		context['bids'] = self.object.Bids.all().order_by('-amount')
		context['cancel_form'] = CancelAuctionForm()
		return context

	def post(self, request, *args, **kwargs):
		artwork = self.get_object()
		if request.POST.get("cancel_auction"):
			artwork.cancel_auction()
			messages.success(request, 'The auction has been cancelled.')
			return redirect('app:artwork_manage', pk=artwork.pk)
		return self.get(request, *args, **kwargs)


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
