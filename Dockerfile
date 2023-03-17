# Usar una imagen base de Python 3
FROM python:3.10

# Crear un directorio de trabajo llamado code
RUN mkdir /code
WORKDIR /code

# Copiar el archivo requirements.txt al directorio code
COPY requirements.txt /code/

# Instalar las dependencias con pip
RUN pip install -r requirements.txt

# Copiar el resto del código al directorio code
COPY . /code/