from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_is_staff"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar_s3_key",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
