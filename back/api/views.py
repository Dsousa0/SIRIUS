from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .serializers import ArquivoSerializer, FileUploadSerializer, AnalyzeRequestSerializer, ChatSerializer, MensagemSerializer
from .models import Arquivo, Chat, Mensagem
import pandas as pd
import pdfplumber
import docx
import io
import uuid
from django.conf import settings
from openai import OpenAI
from deep_translator import GoogleTranslator
from rest_framework.permissions import IsAuthenticated

# Configuração da API OpenRouter
client = OpenAI(api_key='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', base_url="https://openrouter.ai/api/v1")

class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]  

    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Use POST para enviar arquivos."})
        
    def post(self, request, *args, **kwargs):
        serializer = ArquivoSerializer(data=request.data)
        if serializer.is_valid():
            arquivo = serializer.save()
            return Response({
                "message": "Arquivo enviado com sucesso!",
                "file_id": arquivo.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class AnalyzeDataView(APIView): 
    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        if serializer.is_valid():
            file_id = serializer.validated_data.get('file_id', None)
            prompt = serializer.validated_data['prompt']
        
            df_str = ""
            if file_id:
                try:
                    arquivo = Arquivo.objects.get(id=file_id)
                    path = arquivo.arquivo.path
                    if path.endswith('.csv'):
                        df = pd.read_csv(path)
                        df_str = df.to_string()
                    elif path.endswith('.xlsx'):
                        df = pd.read_excel(path, engine='openpyxl')
                        df_str = df.to_string()
                    elif path.endswith('.pdf'):
                        with pdfplumber.open(path) as pdf:
                            df_str = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                    elif path.endswith('.docx'):
                        doc = docx.Document(path)
                        df_str = "\n".join([para.text for para in doc.paragraphs])
                    elif path.endswith('.txt'):
                        with open(path, 'r', encoding='utf-8') as file:
                            df_str = file.read()
                    else:
                        df_str = "[Arquivo genérico recebido. Nenhuma leitura automatizada disponível.]"
                except Arquivo.DoesNotExist:
                    return Response({"error": "Arquivo não encontrado"}, status=status.HTTP_404_NOT_FOUND)

            final_prompt = f"{df_str}\n\n{prompt}" if df_str else prompt

            response = client.chat.completions.create(
                model="qwen/qwen3-4b:free",
                messages=[{"role": "user", "content": final_prompt}]
            )

            return Response({"response": response.choices[0].message.content})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteFileView(APIView):
    def delete(self, request):
        file_id = request.query_params.get("file_id", None)
        if not file_id:
            return Response({"error": "File_id  não encontrado"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            arquivo = Arquivo.objects.get(id=file_id)
            arquivo.arquivo.delete(save=False)
            arquivo.delete()
            return Response({"message": "Arquivo deletado com sucesso!"})

        except Arquivo.DoesNotExist:
            return Response({"error": "Arquivo não encontrado"}, status=status.HTTP_404_NOT_FOUND)

class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MensagemListCreateView(generics.ListCreateAPIView):
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Mensagem.objects.filter(chat__id=chat_id, chat__user=self.request.user)

    def perform_create(self, serializer):
        chat = Chat.objects.get(id=self.kwargs['chat_id'], user=self.request.user)
        serializer.save(chat=chat)

class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

class FreeChatView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        chat_id = request.data.get("chat_id")

        if not prompt or not chat_id:
            return Response({"error": "Prompt e chat_id são obrigatórios."}, status=400)

        mensagens = Mensagem.objects.filter(chat_id=chat_id).order_by('timestamp')
        history = [{"role": m.role, "content": m.content} for m in mensagens]

        response = client.chat.completions.create(
            model="qwen/qwen3-4b:free",
            messages=history + [{"role": "user", "content": prompt}]
        )
        return Response({"response": response.choices[0].message.content})