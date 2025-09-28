"""
Modelo de datos para eventos (Event) en el pipeline UFC ETL.
Define los atributos principales de un evento y métodos para su serialización y deserialización.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    Modelo de datos para un evento.
    Incluye información básica de eventos de UFC, permitiendo su manejo estructurado.
    """
    event_id: str
    name: str
    date: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convierte la instancia del evento a un diccionario, excluyendo los atributos con valor None.
        Returns:
            dict: Representación en diccionario del evento.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """
        Crea una instancia de Event a partir de un diccionario, utilizando solo las claves válidas.
        Args:
            data (dict): Diccionario con los datos del evento.
        Returns:
            Event: Instancia creada a partir del diccionario.
        """
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})