from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    conversa = models.TextField()  # Última conversación establecida con chatGPT
    reset_conversation = models.BooleanField(default=False)  # Indica si se debe reiniciar la conversación
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'
    
class Persona(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=10)
    peso = models.IntegerField()
    altura = models.IntegerField()
    tn_peso = models.DateTimeField(auto_now_add=True)


#python manage.py makemigrations
#python manage.py migrate
#python manage.py showmigrations

