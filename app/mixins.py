from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ArtworkFilterForm
from .models import Customer
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied

class ArtworkFilterMixin:
	def get_queryset(self):
		queryset = super().get_queryset()
		self.form = ArtworkFilterForm(self.request.GET or None)

		if self.form.is_valid():
			query = self.form.cleaned_data.get('q')
			category = self.form.cleaned_data.get('category')
			artist = self.form.cleaned_data.get('artist')
			sort_by = self.form.cleaned_data.get('sort_by')
			
			if query:
				queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
			if category:
				queryset = queryset.filter(category=category)
			if artist:
				queryset = queryset.filter(artist=artist)
			if sort_by:
				if sort_by == 'price':
					queryset = queryset.annotate(highest_bid=Max('Bids__amount')).order_by('-highest_bid')
				elif sort_by == 'auction_end':
					queryset = queryset.order_by('auction_end')
					
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = self.form
		return context

class OwnedBySellerRequired:
	def dispatch(self, request, *args, **kwargs):
		artwork = self.get_object()
		if not request.user.is_authenticated or artwork.seller.user != request.user:
			raise PermissionDenied("You do not have permission to access this page.")
		return super().dispatch(request, *args, **kwargs)

class SellerRequired:
	def dispatch(self, request, *args, **kwargs):
		user = request.user
		if not user.is_authenticated :
			raise PermissionDenied("You need to login to create an artwork")
		
		customer = Customer.objects.get(user=user)
		if not customer.is_seller:
			raise PermissionDenied("You need to be a seller to post an artork")

		return super().dispatch(request, *args, **kwargs)

