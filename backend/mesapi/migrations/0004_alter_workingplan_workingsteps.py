# Generated by Django 3.2.3 on 2021-05-19 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mesapi', '0003_auto_20210519_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workingplan',
            name='workingSteps',
            field=models.ManyToManyField(blank=True, to='mesapi.WorkingStep'),
        ),
    ]