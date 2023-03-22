# Usar una imagen base de Python 3
FROM python:3.10

COPY mileto.sql /mileto.sql

# Crear un directorio de trabajo llamado code
RUN mkdir /code
WORKDIR /code

# Copiar el archivo requirements.txt al directorio code
COPY requirements.txt /code/

# Instalar las dependencias con pip
RUN pip install -r requirements.txt

# Copiar el script wait-for-it.sh en la imagen de django
COPY wait-for-it.sh /wait-for-it.sh
# Darle permisos de ejecución al script
RUN chmod +x /wait-for-it.sh

# Copiar el resto del código al directorio code
COPY . /code/


EXPOSE 5432
EXPOSE 8000


# Ejecutar el comando gunicorn para iniciar la aplicación
#CMD ["python", "manage.py", "migrate"]; ["gunicorn", "--bind", "0.0.0.0:8000", "mileto.wsgi"]; ["/wait-for-it.sh", "db:5432", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["sh", "/docker-entrypoint-initdb.d/restore.sh"]