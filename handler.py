import json
import requests
from bs4 import BeautifulSoup
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def scrape_sismos(event, context):
    url = 'https://ultimosismo.igp.gob.pe/productos/reportes-sismicos'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar la tabla de sismos (inspecciona la página para obtener el selector correcto)
        # Este es un ejemplo, el selector puede variar. Normalmente es una tabla con clase 'table'
        table = soup.find('table')
        rows = table.find_all('tr')[1:11]  # Omitir cabecera y tomar 10 filas

        saved_items = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                # Ajusta los índices según la estructura de la tabla
                fecha_hora = cols[0].text.strip()
                magnitud = cols[1].text.strip()
                profundidad = cols[2].text.strip()
                ubicacion = cols[3].text.strip()
                referencia = cols[4].text.strip() if len(cols) > 4 else ''

                item = {
                    'id': str(uuid.uuid4()),
                    'fecha_hora': fecha_hora,
                    'magnitud': magnitud,
                    'profundidad': profundidad,
                    'ubicacion': ubicacion,
                    'referencia': referencia,
                    'fecha_registro': datetime.now().isoformat()
                }

                # Guardar en DynamoDB
                table.put_item(Item=item)
                saved_items.append(item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Se guardaron {len(saved_items)} sismos',
                'data': saved_items
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
