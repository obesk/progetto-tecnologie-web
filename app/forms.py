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
		fields = ['name', 'artist', 'category', 'publication_date', 'images']
		widgets = {
			'publication_date': forms.DateInput(attrs={'type': 'date'}),
		}