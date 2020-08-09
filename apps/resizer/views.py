from django.views.generic import ListView, FormView
from django.views.generic.detail import BaseDetailView
from django.urls import reverse

from .models import UploadImage
from .forms import UploadImageForm, ResizeImageForm
from image_resizer import settings
from .utils import get_resize_postfix_path, resize_and_save_image


class ImageListView(ListView):
    template_name = 'index.html'
    model = UploadImage
    context_object_name = 'images'


class ImageDetailView(FormView, BaseDetailView):
    template_name = 'image_details.html'
    context_object_name = 'image'
    form_class = ResizeImageForm
    model = UploadImage

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super().post(*args, **kwargs)

    def get_form_kwargs(self):
        obj = self.get_object()
        original_image = obj.original_image
        resized_image = obj.resized_image
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'initial':{
                'width': resized_image.width,
                'height': resized_image.height,
                'sizes': 'ALL',
            },
            'max_value':{
                'width': original_image.width,
                'height': original_image.height,
            }
        })
        return kwargs

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        width = cleaned_data['width']
        height = cleaned_data['height']
        obj = self.get_object()

        resize_image_path = get_resize_postfix_path(obj.original_image.name)
        resize_image_filepath = f'{settings.MEDIA_ROOT}{resize_image_path}'
        resize_and_save_image(obj.original_image, (width, height),  resize_image_filepath)
        obj.resized_image = resize_image_path
        obj.save()

        self.success_url = reverse('image-detail', args=[self.object.id])
        return super().form_valid(form)


class UploadImageFormView(FormView):
    template_name = 'upload_image.html'
    form_class = UploadImageForm

    def form_valid(self, form):
        cleaned_data = form.cleaned_data

        image = UploadImage.objects.create(
            original_image=cleaned_data['image']
        )
        image.resized_image = image.original_image
        image.image_name =  image.original_image.name.split('/')[-1]
        image.save()

        self.success_url = reverse('image-detail', args=[image.id])
        return super().form_valid(form)
