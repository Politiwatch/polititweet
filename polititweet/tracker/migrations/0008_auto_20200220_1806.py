# Generated by Django 2.2.5 on 2020-02-20 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0007_auto_20200130_2019"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="tweet",
            name="tracker_twe_modifie_44db67_idx",
        ),
        migrations.AddIndex(
            model_name="tweet",
            index=models.Index(
                fields=["-modified_date", "full_text", "deleted"],
                name="tracker_twe_modifie_18bb4e_idx",
            ),
        ),
    ]
