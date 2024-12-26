from django.urls import path
from .views import (
    GenerateImage,
)


urlpatterns = [
    path("generate", GenerateImage.as_view()),  # translate pdf ...
]
