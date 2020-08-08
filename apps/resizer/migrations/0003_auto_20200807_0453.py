# Generated by Django 3.1 on 2020-08-07 04:53

from django.db import migrations, models


def set_images_names(apps, schema_editor):
    UploadImage = apps.get_model('resizer', 'UploadImage')
    for image in UploadImage.objects.all():
        image_name = image.original_image.name.split('/')[-1]
        image.image_name = image_name
        image.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resizer', '0002_auto_20200807_0444'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadimage',
            name='image_name',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.RunPython(set_images_names),
    ]
