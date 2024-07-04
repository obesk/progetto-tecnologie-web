from django import forms
from django.urls import reverse_lazy
from django.utils import timezone
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


class CancelAuctionForm(forms.Form):
    cancel_auction = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class ArtworkForm(forms.ModelForm):
    images = MultipleFileField()
    template_name = "app/create_artwork.html"

    class Meta:
        model = Artwork
        fields = [
            "name",
            "artist",
            "category",
            "description",
            "publication_date",
            "images",
            "auction_end",
        ]
        widgets = {
            "publication_date": forms.DateInput(attrs={"type": "date"}),
            "auction_end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["images"].required = False

    def clean_publication_date(self):
        publication_date = self.cleaned_data.get("publication_date")
        if publication_date > timezone.now().date():
            raise forms.ValidationError("The publication date must be in the past.")
        return publication_date

    def clean_auction_end(self):
        auction_end = self.cleaned_data.get("auction_end")
        if auction_end < timezone.now() + timezone.timedelta(hours=1):
            raise forms.ValidationError(
                "The auction end date must be at least an hour from now."
            )
        return auction_end


class ArtworkFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by title or description...",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Category",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        required=False,
        label="Artist",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort_by = forms.ChoiceField(
        choices=[
            ("", "Sort by"),
            ("price", "Price"),
            ("auction_end", "Auction End Date"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
