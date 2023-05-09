from django.urls import path
from .views import MOD

urlpatterns = [
    path("", MOD.as_view()),
]
