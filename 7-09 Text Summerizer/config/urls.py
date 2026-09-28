from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("summarizer.urls")),
    path("", include("summarizer.web_urls")),
]
