from django.urls import path
from .views import FileUploadView, AnalyzeDataView, DeleteFileView, ChatListCreateView, MensagemListCreateView, ChatDetailView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('analyze/', AnalyzeDataView.as_view(), name='analyze-data'),
    path('delete/', DeleteFileView.as_view(), name='delete-file'),
    path('chats/', ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:chat_id>/mensagens/', MensagemListCreateView.as_view(), name='mensagem-list-create'),
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'), 
]
