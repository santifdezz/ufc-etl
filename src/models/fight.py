"""
Modelo de datos para peleas (Fight) en el pipeline UFC ETL.
Incluye atributos de identificación, detalles, estadísticas y métodos de serialización/deserialización.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Fight:
    """
    Modelo de datos para una pelea.
    Incluye información básica, detalles y estadísticas de la pelea, permitiendo su manejo estructurado.
    """
    event_id: str
    fight_id: str
    fight_order: Optional[int] = None
    
    # Fighters
    red_id: Optional[str] = None
    red_name: Optional[str] = None
    blue_id: Optional[str] = None
    blue_name: Optional[str] = None
    winner_id: Optional[str] = None
    
    # Fight details
    weight_class: Optional[str] = None
    referee: Optional[str] = None
    round: Optional[str] = None
    time: Optional[str] = None
    time_format: Optional[str] = None
    method: Optional[str] = None
    details: Optional[str] = None
    bonus: Optional[list[str]] = None
    
    # Statistics
    kd1: str = '0'
    kd2: str = '0'
    str1: str = '0'
    str2: str = '0'
    td1: str = '0'
    td2: str = '0'
    sub1: str = '0'
    sub2: str = '0'
    
    # Extended stats
    control_time1: Optional[str] = None
    control_time2: Optional[str] = None
    sig_head1: Optional[str] = None
    sig_head2: Optional[str] = None
    sig_body1: Optional[str] = None
    sig_body2: Optional[str] = None
    sig_leg1: Optional[str] = None
    sig_leg2: Optional[str] = None
    total_str1: Optional[str] = None
    total_str2: Optional[str] = None
    pass1: Optional[str] = None
    pass2: Optional[str] = None
    rev1: Optional[str] = None
    rev2: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convierte la instancia de la pelea a un diccionario, incluyendo todos los atributos.
        Returns:
            dict: Representación en diccionario de la pelea.
        """
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Fight':
        """
        Crea una instancia de Fight a partir de un diccionario, utilizando solo las claves válidas.
        Args:
            data (dict): Diccionario con los datos de la pelea.
        Returns:
            Fight: Instancia creada a partir del diccionario.
        """
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})