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
        raise HTTPException(status_code=400, detail=str(e))


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
        #print("La capacidad no puede ser menos que el número de participantes")
        raise HTTPException(status_code=400, detail="No se inserta porqe la capacidad nueva es menor")
        #return existing_event

    container.replace_item(item=event_id, body=existing_event)
    return existing_event

#Eliminar evento
@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: str):
    try:
        container.delete_item(item=event_id, partition_key=event_id)
        return
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))


###Endpoints de Participantes
@app.post("/events/{event_id}/participants/", response_model=Participante, status_code=201)
def add_participante(event_id: str, participant: Participante):
    try:
        event=container.read_item(item=event_id, partition_key=event_id)
        
        if len(event['participants']) >= event['capacity']:
            raise HTTPException(status_code=400, detail='Capacidad máxima del evento alcanzada')
        
        if any(p['id'] == participant.id for p in event['participants']):
            raise HTTPException(status_code=400, detail='El participante {p} ya está inscrito')

        event['participants'].append(participant.dict())
        container.replace_item(item=event_id, body=event)
        
        breakpoint()
        return participant
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events/{event_id}/participants/{participant_id}")
def get_participant(event_id: str, participant_id: str):

    try:
        event= container.read_item(item=event_id, partition_key=event_id)
        #for p in event['participants']:
            #if p['id'] == participant.id
        participant = next((p for p in event['participants'] if p['id'] == participant_id), None) #método que itera listas
        if participant:
            return participant
        else:
            raise HTTPException(status_code=400, detail='Participante no encontrado')
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events/{event_id}/participants/", response_model=List[Participante])
def list_participants(event_id: str):

    try:
        event = container.read_item(item=event_id, partition_key=event_id)
        
        participants = event.get('participants', [])
        return participants
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/events/{event_id}/participants/{participant_id}", response_model=Participante)
def update_participant(event_id: str, participant_id: str, update_participant: Participante):
    try:
        event= container.read_item(item=event_id, partition_key=event_id)
        #for p in event['participants']:
            #if p['id'] == participant.id
        participant = next((p for p in event['participants'] if p['id'] == participant_id), None) #método que itera listas
        if not participant:
            raise HTTPException(status_code=400, detail='Participante no encontrado')

        participant.update(update_participant.dict(exclude_unset=True))

        # lista_nueva[]
        # for p in event['participants']:
        #     if p['id'] != participant_id:
        #         lista_nueva.append(p)
        #     else:
        #         lista_nueva.append(participant)

        event['participants'] = [p if p['id'] != participant_id else participant for p in event['participants']]
        container.replace_item(item=event_id, body=event)

        return participant
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))


#delete participante
@app.delete("/events/{event_id}/participants/{participant_id}")#rutas del evento
def delete_participant(event_id: str, participant_id: str):
    try:
        event= container.read_item(item=event_id, partition_key=event_id) #obtenie el id del evento
        participant = next((p for p in event['participants'] if p['id'] == participant_id), None) #método que itera listas
        
        if not participant:
            raise HTTPException(status_code=400, detail='Participante no encontrado')
        
        event['participants'] = [p for p in event['participants'] if p['id'] != participant_id]
        container.replace_item(item=event_id, body=event)

        return
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

