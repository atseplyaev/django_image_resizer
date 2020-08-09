import requests
from django.core.files.images import ImageFile
import io
from PIL import Image, ImageFile as pil_image_file

pil_image_file.LOAD_TRUNCATED_IMAGES = True


def get_image_file_by_url(url):
    r = requests.get(url, timeout=5)
    filename = url.split('/')[-1]
    file = io.BytesIO(r.content)
    return ImageFile(file=file, name=filename)


def diff_percent(old_value, diff):
    return (old_value - diff) / (old_value / 100)


def new_size_image(max_x, x, max_y):
    per_edit = diff_percent(max_x, x)
    y = int(max_y - (max_y / 100 * per_edit))
    return y


def get_resize_postfix_path(orig_path):
    resize_image_path = orig_path.split('.')
    resize_image_path[-2] = f'{resize_image_path[-2]}_resized'
    return  '.'.join(resize_image_path)


def resize_and_save_image(path, sizes: tuple, output_path):
    resize_image = Image.open(path)
    resize_image = resize_image.resize(sizes, Image.ANTIALIAS)
    resize_image.save(output_path)
    return output_path
