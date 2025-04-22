from rest_framework import serializers
from .models import Arquivo, Chat, Mensagem

class ArquivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arquivo
        fields = ['id', 'arquivo', 'data_upload']

class FileUploadSerializer(serializers.Serializer):
   file = serializers.FileField()  
    
class AnalyzeRequestSerializer(serializers.Serializer):
    file_id = serializers.IntegerField(required=False, allow_null=True)
    prompt = serializers.CharField()

class MensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensagem
        fields = ['id', 'chat', 'role', 'content', 'timestamp']
        read_only_fields = ['chat', 'timestamp']



class ChatSerializer(serializers.ModelSerializer):
    mensagens = MensagemSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'mensagens']


