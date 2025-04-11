# Use uma imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta (caso use runserver)
EXPOSE 8000

# Comando para rodar o servidor Django (pode ser substituído por gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
