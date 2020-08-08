import requests
from django.core.files.images import ImageFile
import io


def get_image_file_by_url(url):
    r = requests.get(url, timeout=5)
    filename = url.split('/')[-1]
    file = io.BytesIO(r.content)
    return ImageFile(file=file, name=filename)
