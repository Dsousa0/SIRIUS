from django.db import models
from django.contrib.auth.models import User

class Arquivo(models.Model):
    arquivo = models.FileField(upload_to='uploads/')
    data_upload = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    title = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Chat {self.id}"

class Mensagem(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='mensagens')
    role = models.CharField(max_length=10)  # 'user' ou 'assistant'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)