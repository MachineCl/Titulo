# Generated by Django 4.1 on 2023-07-17 00:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0009_persona_altura_persona_peso'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='fecha_nacimiento',
        ),
    ]
