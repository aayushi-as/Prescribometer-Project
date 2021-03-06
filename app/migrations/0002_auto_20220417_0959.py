# Generated by Django 3.2.11 on 2022-04-17 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='d_contactNo',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='d_email',
            field=models.EmailField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='patients',
            name='contactNo',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='patients',
            name='email',
            field=models.EmailField(max_length=50, unique=True),
        ),
    ]
