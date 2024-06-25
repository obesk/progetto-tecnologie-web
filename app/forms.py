from django import forms
from .models import Artist, Category, Artwork, Photo



class MultipleFileInput(forms.ClearableFileInput):
	allow_multiple_selected = True


class MultipleFileField(forms.FileField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("widget", MultipleFileInput())
		super().__init__(*args, **kwargs)

	def clean(self, data, initial=None):
		single_file_clean = super().clean
		if isinstance(data, (list, tuple)):
			result = [single_file_clean(d, initial) for d in data]
		else:
			result = [single_file_clean(data, initial)]
		return result


class ArtworkForm(forms.ModelForm):
	images = MultipleFileField()
	template_name = "app/create_artwork.html"

	class Meta:
		model = Artwork
		fields = ['name', 'artist', 'category', 'publication_date', 'images', 'auction_end']
		widgets = {
			'publication_date': forms.DateInput(attrs={'type': 'date'}),
			'auction_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
		}


class ArtworkFilterForm(forms.Form):
	q = forms.CharField(required=False, label='Search', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by title or description...'}))
	category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label='Category', widget=forms.Select(attrs={'class': 'form-select'}))
	artist = forms.ModelChoiceField(queryset=Artist.objects.all(), required=False, label='Artist', widget=forms.Select(attrs={'class': 'form-select'}))
	sort_by = forms.ChoiceField(choices=[
		('', 'Sort by'),
		('price', 'Price'),
		('auction_end', 'Auction End Date'),
	], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
