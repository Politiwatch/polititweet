# Generated by Django 2.2.5 on 2020-01-30 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_auto_20200130_2007'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='tweet',
            index=models.Index(fields=['-modified_date'], name='tracker_twe_modifie_44db67_idx'),
        ),
    ]