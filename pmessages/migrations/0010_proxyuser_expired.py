# Generated by Django 2.2.12 on 2020-11-11 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pmessages", "0009_auto_20201108_2304"),
    ]

    operations = [
        migrations.AddField(
            model_name="proxyuser",
            name="expired",
            field=models.BooleanField(default=False),
        ),
    ]
