from django.urls import path
from .views import ask_question

# Define URL patterns for the app
urlpatterns = [
    # Route for handling user questions via POST request
    path("ask/", ask_question),
]
