from django.urls import path
from .views import SummarizeAPIView

urlpatterns = [
    path("summarize/", SummarizeAPIView.as_view(), name="summarize"),
]
