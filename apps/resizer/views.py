from django.views.generic import ListView, DetailView,\
    FormView, UpdateView
from django.views.generic.detail import BaseDetailView

from django.http import HttpResponse
from .models import UploadImage
from .forms import UploadImageForm, ResizeImageForm


class ImageListView(ListView):
    template_name = 'index.html'
    model = UploadImage
    paginate_by = 25
    context_object_name = 'images'


class UploadImageFormView(FormView):
    template_name = 'upload_image.html'
    form_class = UploadImageForm
    success_url = '/'

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        print(form.cleaned_data)
        image = UploadImage.objects.create(
            original_image=cleaned_data['image']
        )
        image.resized_image = image.original_image
        image.image_name =  image.original_image.name.split('/')[-1]
        image.save()
        return super().form_valid(form)
