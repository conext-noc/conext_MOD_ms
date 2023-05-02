from django.urls import path
from .views import MOD, CHECK

urlpatterns = [
    path("", MOD.as_view()),
    path("check/", CHECK.as_view()),
]
