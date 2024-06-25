from .forms import ArtworkFilterForm
from .models import Artwork
from django.db.models import Q, Max

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
