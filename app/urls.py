from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = "app"

urlpatterns = [
	path("artworklist/", ArtworksListView.as_view(), name="artworklist"),
	path("artwork/<pk>", ArtworkDetailView.as_view(), name="artworkdetail"),
	path("create_artwork/", ArtworkCreateView.as_view(), name="create_artwork"),
	path("placebid/", placeBid, name="placebid"),
	path("", homepage, name="homepage"),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
