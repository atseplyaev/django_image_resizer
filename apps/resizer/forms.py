from django import forms
from django.core import validators, exceptions
from image_resizer.settings import MAX_UPLOAD_IMAGE_SIZE
import requests
from .utils import get_image_file_by_url, new_size_image, \
    diff_percent


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


class ResizeImageForm(forms.Form):
    width = forms.IntegerField(min_value=1, required=False)
    height = forms.IntegerField(min_value=1, required=False)

    SIZES_CHOICES = [
        ('ALL', u'Изменение ширины и высоты'),
        ('HEI', u'Изменение высоты'),
        ('WID', u'Изменение ширины'),
    ]
    sizes = forms.ChoiceField(choices=SIZES_CHOICES, widget=forms.RadioSelect)

    width.widget.attrs.update(
        {
            'class': 'form-control w-50',
            'id': 'id_width',
        }
    )
    height.widget.attrs.update(
        {
            'class': 'form-control w-50',
            'id': 'id_height',
        }
    )
    sizes.widget.attrs.update(
        {
            'class': 'form-check-input',
        }
    )

    def __init__(self, *args, **kwargs):
        max_value = kwargs.pop('max_value')
        super().__init__(*args, **kwargs)
        fields = self.fields
        for name, field in fields.items():
            field_max_value = max_value.get(name, None)

            if not field_max_value:
                continue

            field.max_value = field_max_value
            field.validators.append(validators.MaxValueValidator(field_max_value))
            widget = field.widget
            extra_attrs = field.widget_attrs(widget)
            if extra_attrs:
                widget.attrs.update(extra_attrs)

    def clean(self):
        cleaned_data = super().clean()
        height = cleaned_data.get('height')
        width = cleaned_data.get('width')
        sizes = cleaned_data.get('sizes')
        max_width = self.fields['width'].max_value
        max_height = self.fields['height'].max_value
        initial_width = self.initial['width']
        initial_height = self.initial['height']

        if (width and width > max_width) or \
                (height and height > max_height):
            raise forms.ValidationError('Error max value')

        if (width and width == initial_width) and \
                (height and height == initial_height):
            raise forms.ValidationError('The values were not changed')

        if sizes == 'ALL':
            width_diff = diff_percent(max_width, width)
            height_diff = diff_percent(max_height, height)

            if height_diff > width_diff:
                sizes = 'HEI'
            elif height_diff < width_diff:
                sizes = 'WID'

        if sizes == 'HEI':
            width = new_size_image(max_height, height, max_width)
            cleaned_data['width'] = width

        elif sizes == 'WID':
            height = new_size_image(max_width, width, max_height)
            cleaned_data['height'] = height

        return cleaned_data
