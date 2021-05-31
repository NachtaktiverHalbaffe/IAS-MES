# Generated by Django 3.2.3 on 2021-05-31 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mesapi', '0002_auto_20210531_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignedorder',
            name='costumerNo',
        ),
        migrations.AddField(
            model_name='assignedorder',
            name='costumer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mesapi.costumer'),
        ),
    ]