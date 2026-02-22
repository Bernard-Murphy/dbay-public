# Category default_icon and CategoryItem image_url

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0002_categoryitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="default_icon",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="categoryitem",
            name="image_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
