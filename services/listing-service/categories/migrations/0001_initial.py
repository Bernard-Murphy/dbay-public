# Generated migration for Category model

from django.db import migrations, models
import django_ltree.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=100)),
                ("path", django_ltree.fields.PathField(unique=True)),
                ("icon_url", models.URLField(blank=True, null=True)),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={
                "verbose_name_plural": "categories",
                "ordering": ["path"],
            },
        ),
    ]
