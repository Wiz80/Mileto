from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import FileNotUploadedError
import os


class Google_Cloud_Drive():

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def find_credenciales(self):
        directorio_credenciales = 'credentials_module.json'
        path_to_credenciales = 'C:\\Users\\pc\\Desktop\\Python\\Tesis\\Mileto\\predictions\\Google_Cloud\\'
        return self.find(directorio_credenciales, path_to_credenciales)

    def login(self):
        directorio_credenciales = self.find_credenciales()
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = directorio_credenciales
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(directorio_credenciales)
        
        if gauth.credentials is None:
            gauth.LocalWebserverAuth(port_numbers=[8092])
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
            
        gauth.SaveCredentialsFile(directorio_credenciales)
        credenciales = GoogleDrive(gauth)
        return credenciales

    # SUBIR UN ARCHIVO A DRIVE
    def subir_archivo(self, ruta_archivo,id_folder):
        credenciales = self.login()
        archivo = credenciales.CreateFile({'parents': [{"kind": "drive#fileLink",\
                                                        "id": id_folder}]})
        archivo['title'] = ruta_archivo.split("/")[-1]
        archivo.SetContentFile(ruta_archivo)
        archivo.Upload()


    # DESCARGAR UN ARCHIVO DE DRIVE POR ID
    def bajar_archivo_por_id(self, id_drive,ruta_descarga):
        credenciales = self.login()
        archivo = credenciales.CreateFile({'id': id_drive}) 
        nombre_archivo = archivo['title']
        archivo.GetContentFile(ruta_descarga + nombre_archivo)

    # DESCARGAR UN ARCHIVO DE DRIVE POR NOMBRE
    def bajar_acrchivo_por_nombre(self, nombre_archivo,ruta_descarga):
        credenciales = self.login()
        lista_archivos = credenciales.ListFile({'q': "title = '" + nombre_archivo + "'"}).GetList()
        if not lista_archivos:
            print('No se encontro el archivo: ' + nombre_archivo)
        archivo = credenciales.CreateFile({'id': lista_archivos[0]['id']}) 
        archivo.GetContentFile(ruta_descarga + nombre_archivo)

    # BORRAR/RECUPERAR ARCHIVOS
    def borrar_recuperar(self, id_archivo):
        credenciales = self.login()
        archivo = credenciales.CreateFile({'id': id_archivo})
        # MOVER A BASURERO
        archivo.Trash()
        # SACAR DE BASURERO
        archivo.UnTrash()
        # ELIMINAR PERMANENTEMENTE
        archivo.Delete()


    def busca(self,query):
        resultado = []
        credenciales = self.login()
        # Archivos con el nombre 'mooncode': title = 'mooncode'
        # Archivos que contengan 'mooncode' y 'mooncoders': title contains 'mooncode' and title contains 'mooncoders'
        # Archivos que NO contengan 'mooncode': not title contains 'mooncode'
        # Archivos que contengan 'mooncode' dentro del archivo: fullText contains 'mooncode'
        # Archivos en el basurero: trashed=true
        # Archivos que se llamen 'mooncode' y no esten en el basurero: title = 'mooncode' and trashed = false
        lista_archivos = credenciales.ListFile({'q': query}).GetList()
        for f in lista_archivos:
            # ID Drive
            print('ID Drive:',f['id'])
            # Link de visualizacion embebido
            print('Link de visualizacion embebido:',f['embedLink'])
            # Link de descarga
            print('Link de descarga:',f['downloadUrl'])
            # Nombre del archivo
            print('Nombre del archivo:',f['title'])
            # Tipo de archivo
            print('Tipo de archivo:',f['mimeType'])
            # Esta en el basurero
            print('Esta en el basurero:',f['labels']['trashed'])
            # Fecha de creacion
            print('Fecha de creacion:',f['createdDate'])
            # Fecha de ultima modificacion
            print('Fecha de ultima modificacion:',f['modifiedDate'])
            # Version
            print('Version:',f['version'])
            # Tamanio
            print('Tamanio:',f['fileSize'])
            
            return f['id']
        

    # MOVER ARCHIVO
    def mover_archivo(self,id_archivo,id_folder):
        credenciales = self.login()
        archivo = credenciales.CreateFile({'id': id_archivo})
        propiedades_ocultas = archivo['parents']
        archivo['parents'] = [{'isRoot': False, 
                            'kind': 'drive#parentReference', 
                            'id': id_folder, 
                            'selfLink': 'https://www.googleapis.com/drive/v2/files/' + id_archivo + '/parents/' + id_folder,
                            'parentLink': 'https://www.googleapis.com/drive/v2/files/' + id_folder}]
        archivo.Upload(param={'supportsTeamDrives': True})
        #Al mover un archivo este conserva el id
