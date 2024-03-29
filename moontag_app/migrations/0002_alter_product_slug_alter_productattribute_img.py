# Generated by Django 4.2.7 on 2023-12-27 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moontag_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=200),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='media/product_images/%Y/%m/%d'),
        ),
    ]
