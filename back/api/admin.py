from django.contrib import admin
from .models import Arquivo, Chat, Mensagem

# Register your models here.
admin.site.register(Arquivo)
admin.site.register(Chat) 
admin.site.register(Mensagem) 