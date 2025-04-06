from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .serializers import ArquivoSerializer, FileUploadSerializer, AnalyzeRequestSerializer, ChatSerializer, MensagemSerializer
from.models import Arquivo, Chat, Mensagem
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
client = OpenAI(api_key=settings.OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Adiciona suporte para upload de arquivos

    
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
            file_id = serializer.validated_data['file_id']
            prompt = serializer.validated_data['prompt']
          
            try:
                arquivo = Arquivo.objects.get(id=file_id)
            except Arquivo.DoesNotExist:
                return Response({"error": "Arquivo não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                path = arquivo.arquivo.path
                if path.endswith('.csv'):
                    df = pd.read_csv(path)
                    df_str = df.to_string()
                elif path.endswith('.xlsx'):
                    df = pd.read_excel(path, engine='openpyxl')
                    df_str = df.to_string()
                elif path.endswith('.pdf'):
                    with pdfplumber.open(path) as pdf:
                        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                    df_str = text
                elif path.endswith('.docx'):
                    doc = docx.Document(path)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    df_str = text
                elif path.endswith('.txt'):
                    with open(path, 'r', encoding='utf-8') as file:
                        df_str = file.read()
                elif path.endswith('.doc'):
                    return Response({"error": "Formato .doc não suportado diretamente. Converta para .docx"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "Formato de arquivo não suportado"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Erro ao ler o arquivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            full_prompt = f"Aqui estão os dados:\n{df_str}\n\n{prompt}"

            try:
                response = client.chat.completions.create(
                    model="google/gemma-3-27b-it:free",
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                insights = response.choices[0].message.content.strip()
                return Response({"insights": insights})
            except Exception as e:
                return Response({"error": f"Erro ao se comunicar com OpenRouter: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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