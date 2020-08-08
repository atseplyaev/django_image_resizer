from django import forms
from django.core import validators, exceptions
from image_resizer.settings import MAX_UPLOAD_IMAGE_SIZE
import requests
from .utils import get_image_file_by_url


class URLImageValidator:
    IMAGE_URL_ENDSWITH = (
        '.jpg',
        '.jpeg',
        '.png',
        '.gif',
    )

    def __call__(self, url):
        if not url:
            return

        if not url.endswith(self.IMAGE_URL_ENDSWITH):
            raise forms.ValidationError('URL: The provided link does not point to the image')

        try:
            r = requests.head(url, timeout=5)
        except (requests.Timeout, requests.ConnectionError):
            raise forms.ValidationError('URL: The server is not available')

        if r.status_code != 200:
            raise forms.ValidationError('URL: Connection error')

        content_type = r.headers.get('Content-Type', "")
        print(content_type)
        if not content_type or not content_type.startswith('image/'):
            raise forms.ValidationError('URL: Upload type not image')

        size_file = int(r.headers.get('Content-Length', 0))

        if not size_file:
            raise forms.ValidationError('URL: Error upload file')

        if size_file > MAX_UPLOAD_IMAGE_SIZE:
            raise forms.ValidationError('URL: File size over 4 Mb')



class UploadImageForm(forms.Form):
    url = forms.URLField(required=False, validators=[URLImageValidator()])
    image = forms.ImageField(required=False)

    url.widget.attrs.update(
        {
            'class': 'form-control w-50',
            'id': 'id_url',
        }
    )
    image.widget.attrs.update(
        {
            'class': 'form-control w-50',
            'id': 'id_image',
        }
    )

    def clean_image(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        if not image:
            return
        if image.size > MAX_UPLOAD_IMAGE_SIZE:
            raise forms.ValidationError('Image: File size over 4 Mb')

        return image

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        url = cleaned_data.get('url')

        if self.errors:
            return

        if not image and not url:
            raise forms.ValidationError(
                "The form fields are not filled in."
                "Fill in one field on the form: either a link or a file."
            )
        if image and url:
            raise forms.ValidationError(
                "Both fields are filled in."
                "Fill in one field on the form: either a link or a file."
            )
        if url:
            image = get_image_file_by_url(url)
            cleaned_data['image'] = image

        return cleaned_data
