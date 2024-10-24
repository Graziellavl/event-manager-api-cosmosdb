#Contiene la definición de las rutas del CRUD de eventos y participantes
from fastapi import FastAPI, HTTPException, Query, Path
from typing import List, Optional
from database import container
from models import Evento, Participante
from azure.cosmos import exceptions
from datetime import datetime

app = FastAPI(title="API de Gestión de Eventos y Participantes")

#Endpoint de eventos
@app.get("/") #La raiz
def home():
    return "Hola Mundo"

#Crear evento
@app.post("/events/", response_model=Evento, status_code=201)
def create_event(event: Evento):#Se crea el model evento
    try:
        container.create_item(body=event.dict()) #Se pasa el evento y se transforma a un diccionario
        return event
    except exceptions.CosmosResourceExistsError:
        raise HTTPException(status_code=400, detail="El evento con este ID ya existe.")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=tr(e))

#Obtener evento por id
@app.get("/events/{event_id}", response_model=Evento)
def get_event(event_id: str=Path(..., description="ID del evento a recuperar")):
    try:
        event = container.read_item(item=event_id, partition_key=event_id)
        return event
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="El evento no se ha encontrado.")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=tr(e))


#Listar todos los eventos
@app.get("/events/", response_model=List[Evento])
def get_event():
    query = "select * from c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    return items

#Update
@app.put("/events/{event_id}", response_model = Evento)
def update_event(event_id:str, updated_event:Evento):
    existing_event = container.read_item(item=event_id, partition_key = event_id)
    #exclude_unset:Que al actualizar no impacte los valores de los campos que no han sido devueltos en la petición
    existing_event.update(updated_event.dict(exclude_unset=True))
    
    if existing_event['capacity'] < len(existing_event['participants']):
        print("La capacidad no puede ser menos que el número de participantes")
        return existing_event

    container.replace_item(item=event_id, body=existing_event)
    return existing_event