import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do cliente DO Spaces
session = boto3.session.Session()
client = session.client('s3',
    region_name=os.getenv('DO_SPACES_REGION'),
    endpoint_url=os.getenv('DO_SPACES_ENDPOINT'),
    aws_access_key_id=os.getenv('DO_SPACES_KEY'),
    aws_secret_access_key=os.getenv('DO_SPACES_SECRET'),
    config=Config(s3={'addressing_style': 'virtual'})
)

def upload_file(local_file, spaces_path):
    """Faz upload de um arquivo para o DO Spaces"""
    try:
        bucket = os.getenv('DO_SPACES_BUCKET')
        folder = os.getenv('DO_SPACES_FOLDER')
        full_path = f"{folder}/{spaces_path}"
        
        print(f"Fazendo upload de {local_file} para {full_path}")
        client.upload_file(local_file, bucket, full_path)
        print(f"Upload concluído com sucesso!")
        
        # Verifica se o arquivo foi realmente enviado
        try:
            client.head_object(Bucket=bucket, Key=full_path)
            print(f"Arquivo verificado com sucesso em {full_path}")
        except Exception as e:
            print(f"Erro ao verificar arquivo: {str(e)}")
            
    except Exception as e:
        print(f"Erro ao fazer upload: {str(e)}")

def main():
    # Lista de arquivos para upload
    files = [
        {
            'local': 'documentos/cnh.jpg',
            'spaces': '1747591031684734949-rg2.jpg'
        },
        {
            'local': 'documentos/cch.jpg',
            'spaces': '1747591052268341173-residencia2.jpg'
        },
        {
            'local': 'documentos/residencia.jpg',
            'spaces': '1747591067021033417-cc2.jpg'
        }
    ]
    
    # Faz upload de cada arquivo
    for file in files:
        if os.path.exists(file['local']):
            upload_file(file['local'], file['spaces'])
        else:
            print(f"Arquivo local não encontrado: {file['local']}")

if __name__ == "__main__":
    main() 