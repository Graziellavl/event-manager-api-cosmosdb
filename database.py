from azure.cosmos import CosmosClient, exceptions

cosmos_endpoint = 'https://acdbgvldev.documents.azure.com:443/'
cosmos_key = '6RWzeEoyI8Xuxq82wbz9S3O0L2RGVplh8XtFWwBN3AaSCtw6f2318d5YxOJsbudfGXJO0yA2Pg7LACDbhp5LVA=='
database_name = 'test_db'
container = 'eventos'

client = CosmosClient(cosmos_endpoint, cosmos_key)

# Crear o obtener la base de datos
try:
    database = client.create_database_if_not_exists(id=database_name)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(database_name)


# Crear u obtener el contenedor
try:
    container = database.create_container_if_not_exists(
    id=container, 
    partition_key={'paths': ['/id'], 'kind': 'Hash'},
    offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container)