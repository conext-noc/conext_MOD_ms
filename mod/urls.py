from django.urls import path
from .views import MOD, MODDashboard

urlpatterns = [
    path("", MOD.as_view()),
    path("dashboard", MODDashboard.as_view()),
]
