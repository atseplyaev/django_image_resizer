from django.urls import path
from .views import ImageListView, ImageDetailView, \
    UploadImageFormView

urlpatterns = [
    path('', ImageListView.as_view(), name='index'),
    path('<int:pk>/', ImageDetailView.as_view(), name='image-detail'),
    path('upload/', UploadImageFormView.as_view(), name='upload'),
]
