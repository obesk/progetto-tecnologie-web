from django.contrib import admin
from .models import Artist, Artwork, Category, Photo


admin.site.register(Artist)
admin.site.register(Artwork)
admin.site.register(Category)
admin.site.register(Photo)