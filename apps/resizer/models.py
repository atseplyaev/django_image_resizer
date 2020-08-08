from django.db import models


class UploadImage(models.Model):
    image_name = models.CharField(max_length=128)
    resized_image = models.ImageField(upload_to='%Y/%m/%d', null=True)
    original_image = models.ImageField(upload_to='%Y/%m/%d')

    def __str__(self):
        return self.original_image
