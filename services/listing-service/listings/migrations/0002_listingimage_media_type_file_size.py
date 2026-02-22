# Generated manually for media_type and file_size

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingimage',
            name='media_type',
            field=models.CharField(choices=[('image', 'Image'), ('video', 'Video')], default='image', max_length=10),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='file_size',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
