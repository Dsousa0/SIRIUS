# Generated by Django 5.1.7 on 2025-04-13 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_chat_mensagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensagem',
            name='role',
            field=models.CharField(max_length=10),
        ),
    ]
