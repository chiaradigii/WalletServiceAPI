# Generated by Django 5.0.4 on 2024-04-13 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('client', 'Client'), ('merchant', 'Merchant')], default='client', max_length=10),
        ),
    ]
