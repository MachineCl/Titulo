# Generated by Django 4.1 on 2023-07-05 02:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatbot', '0003_chat_reset_conversation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_nacimiento', models.DateField()),
                ('genero', models.CharField(max_length=10)),
                ('peso', models.DecimalField(decimal_places=2, max_digits=5)),
                ('altura', models.DecimalField(decimal_places=2, max_digits=4)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
