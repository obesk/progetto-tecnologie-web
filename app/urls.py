from django.urls import path
from .views import *

app_name = "app"

urlpatterns = [
	path("artworklist/", ArtworksListView.as_view(), name="artworklist"),
	path("create_artwork/", ArtworkCreateView.as_view(), name="create_artwork"),
]
