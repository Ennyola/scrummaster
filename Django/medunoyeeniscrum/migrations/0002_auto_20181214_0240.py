# Generated by Django 2.0.4 on 2018-12-14 01:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medunoyeeniscrum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrumgoal',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medunoyeeniscrum.ScrumUser'),
        ),
    ]
