# Generated by Django 5.2 on 2025-04-05 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='', verbose_name='документ')),
                ('word_frequency', models.JSONField()),
            ],
        ),
    ]
