from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from channels.layers import get_channel_layer

from .models import Artwork, Photo, Bid, AppUser
from .forms import ArtworkForm, CancelAuctionForm
from .mixins import ArtworkFilterMixin, OwnedBySellerRequired, SellerRequired, OwnedBySellerRequired, CustomerRequired

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
		self.seller = get_object_or_404(AppUser, id=self.kwargs.get('seller_id'))
		queryset = super().get_queryset()
		return queryset.filter(seller=self.seller, status=Artwork.Status.AUCTIONING)
	
	def get_context_data(self, **kwargs):
		user  = self.request.user
		context = super().get_context_data(**kwargs)
		context['title'] = f"{self.seller.user.username}'s Auctioning Artworks"
		context['seller_name'] = self.seller.user.username
		return context

class SellerArtworkManagement(SellerRequired, ArtworkFilterMixin, ListView):
	model = Artwork
	template_name = "app/seller_manage_artworks.html"
	
	def get_queryset(self):
		self.seller = get_object_or_404(AppUser, user  = self.request.user)

		queryset = super().get_queryset()
		return queryset.filter(seller=self.seller)
	
	def get_context_data(self, **kwargs):
		user  = self.request.user
		context = super().get_context_data(**kwargs)
		context['title'] = f"{self.seller.user.username}'s Artworks Management"
		context['seller_name'] = self.seller.user.username
		return context

class CustomerProfile(TemplateView, CustomerRequired):
	model = AppUser
	template_name = "app/customer_profile.html"
	
	def get_context_data(self, **kwargs):
		customer = self.request.user.appuser
		bidded_artworks = []
		artworks = Artwork.objects.filter(Bids__customer=customer).distinct().order_by("auction_end")
		for artwork in artworks:
			highest_bid = artwork.Bids.order_by('-amount').first()
			is_winning = highest_bid.customer == customer if highest_bid else False
			customer_bid = artwork.Bids.filter(customer=customer).order_by('-amount').first()
			bidded_artworks.append({
				'artwork': artwork,
				'customer_bid': customer_bid.amount if customer_bid else None,
				'is_winning': is_winning
			})
		context = super().get_context_data(**kwargs)
		context['customer'] = customer
		context['bidded_artworks'] = bidded_artworks
		context['title'] = f"{self.request.user.username}'s Auctioning Artworks"
		return context

def save_uploaded_file(f):
	filename = f"media/app/static/artwork_images/{f.name}"
	with open(filename, "wb+") as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return filename

class ArtworkCreateView(SellerRequired, CreateView):
	form_class = ArtworkForm
	template_name = "app/create_artwork.html"
	success_url = reverse_lazy("app:homepage")

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

			if other_artwork.auction_end:
				time_to_expiry = other_artwork.auction_end - timezone.now()
			else:
				time_to_expiry = timedelta(seconds=0)
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


class SellerArtworkManage(OwnedBySellerRequired, UpdateView):
	model = Artwork
	template_name = "app/artwork_manage.html"
	form_class = ArtworkForm

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
		if 'add_image' in request.FILES:
			for f in request.FILES.getlist('add_image'):
				Photo.objects.create(file=f, artwork=artwork)
		if 'delete_image' in request.POST:
			image_id = request.POST.get('delete_image')
			try:
				photo = Photo.objects.get(id=image_id)
				photo.delete()
				messages.success(request, 'Image deleted successfully.')
			except Photo.DoesNotExist:
				messages.error(request, 'Image does not exist.')
		return self.get(request, *args, **kwargs)

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, 'The artwork has been updated successfully.')
		return response


@login_required
@csrf_protect
def placeBid(request):
	if request.method == 'POST':
		user = request.user
		customer = AppUser.objects.get(user=user)
		artwork_id = request.POST.get('artwork_id')
		artwork = get_object_or_404(Artwork, id=artwork_id)

		if artwork.seller.user == user:
			return JsonResponse({'status': 'error', 'message': "you can't place bids on your own items"})

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
