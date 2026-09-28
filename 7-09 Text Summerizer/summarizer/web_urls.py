from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "index.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
