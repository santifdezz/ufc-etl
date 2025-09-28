"""
Modelo de datos para luchadores (Fighter) en el pipeline UFC ETL.
Define los atributos principales y detallados de un luchador, permitiendo su serialización y deserialización.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Fighter:
    """
    Modelo de datos para un luchador.
    Incluye información básica y estadísticas detalladas, facilitando el manejo estructurado de los datos de luchadores.
    """
    fighter_id: str
    first: Optional[str] = None
    last: Optional[str] = None
    nickname: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    reach: Optional[str] = None
    stance: Optional[str] = None
    wins: Optional[str] = None
    defeats: Optional[str] = None
    draws: Optional[str] = None
    belt: Optional[bool] = None
    
    # Detailed stats
    dob: Optional[str] = None
    slpm: Optional[str] = None
    str_acc: Optional[str] = None
    sapm: Optional[str] = None
    str_def: Optional[str] = None
    td_avg: Optional[str] = None
    td_acc: Optional[str] = None
    td_def: Optional[str] = None
    sub_avg: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convierte la instancia del luchador a un diccionario, excluyendo los atributos con valor None.
        Returns:
            dict: Representación en diccionario del luchador.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Fighter':
        """
        Crea una instancia de Fighter a partir de un diccionario, utilizando solo las claves válidas.
        Args:
            data (dict): Diccionario con los datos del luchador.
        Returns:
            Fighter: Instancia creada a partir del diccionario.
        """
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})