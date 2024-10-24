#La estructura pydantic permite crear la estructura de los datos
from pydantic import BaseModel, Field, EmailStr

#Importar tipos de listas
from typing import List, Optional

class Participante(BaseModel):
    id: str = Field(..., example='p1')
    name: str = Field(..., example='Mikkel')
    mail: EmailStr=Field(..., example='Mikkel@example.com')
    registration_date: str = Field(..., example='2024-10-23T19:00:00Z')

class Evento(BaseModel):
    id: str = Field(..., example= "e1")
    name: str = Field(..., example="Conferencia Tech 2024")
    description: Optional[str] = Field(..., example="Una conferencia sobre las últimas tendencias en tecnología.")
    date: str = Field(..., example="2024-09-15T09:00:00Z")
    location: str = Field(..., example="Centro de Convenciones Ciudad")
    capacity: int = Field(..., ge = 1, example=300)
    participants: List[Participante] = Field(default_factory = list)
