"""
Utilidades para la validación de datos en el proyecto UFC ETL.
Incluye validadores para asegurar la integridad y consistencia de los datos extraídos y procesados.
"""
from typing import Dict, Any, List, Optional
from ..core.exceptions import ValidationError


class DataValidator:
    """
    Clase utilitaria para validar la integridad y consistencia de los datos extraídos.
    Proporciona métodos estáticos para validar entidades como luchadores, eventos y peleas,
    así como conjuntos completos de datos. Lanza excepciones específicas en caso de errores de validación.
    """
    
    @staticmethod
    def validate_fighter(fighter: Dict[str, Any]) -> bool:
        """
        Valida la información de un luchador.
        Verifica que existan los campos obligatorios y que el nombre esté presente de forma adecuada.
        Lanza ValidationError si falta algún campo esencial.
        Args:
            fighter (Dict[str, Any]): Diccionario con los datos del luchador.
        Returns:
            bool: True si la validación es exitosa.
        """
        required_fields = ['fighter_id']
        
        for field in required_fields:
            if not fighter.get(field):
                raise ValidationError(f"Fighter missing required field: {field}")
        
    # Se verifica que al menos existan los componentes mínimos del nombre
        has_name = (fighter.get('first') and fighter.get('last')) or fighter.get('name')
        if not has_name:
            raise ValidationError(f"Fighter {fighter['fighter_id']} missing name information")
        
        return True
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> bool:
        """
        Valida la información de un evento.
        Verifica que existan los campos obligatorios.
        Lanza ValidationError si falta algún campo esencial.
        Args:
            event (Dict[str, Any]): Diccionario con los datos del evento.
        Returns:
            bool: True si la validación es exitosa.
        """
        required_fields = ['event_id', 'name']
        
        for field in required_fields:
            if not event.get(field):
                raise ValidationError(f"Event missing required field: {field}")
        
        return True
    
    @staticmethod
    def validate_fight(fight: Dict[str, Any]) -> bool:
        """
        Valida la información de una pelea.
        Verifica que existan los campos obligatorios.
        Lanza ValidationError si falta algún campo esencial.
        Args:
            fight (Dict[str, Any]): Diccionario con los datos de la pelea.
        Returns:
            bool: True si la validación es exitosa.
        """
        required_fields = ['event_id', 'fight_id']
        
        for field in required_fields:
            if not fight.get(field):
                raise ValidationError(f"Fight missing required field: {field}")
        
        return True
    
    @staticmethod
    def validate_dataset(data: List[Dict[str, Any]], data_type: str) -> Dict[str, int]:
        """
        Valida un conjunto completo de datos de un tipo específico (luchador, evento o pelea).
        Aplica la función de validación correspondiente a cada elemento y recopila estadísticas de éxito.
        Imprime advertencias para los primeros errores encontrados.
        Args:
            data (List[Dict[str, Any]]): Lista de diccionarios con los datos a validar.
            data_type (str): Tipo de datos ('fighter', 'event', 'fight').
        Returns:
            Dict[str, int]: Estadísticas de validación (total, válidos, inválidos, tasa de éxito).
        """
        validation_funcs = {
            'fighter': DataValidator.validate_fighter,
            'event': DataValidator.validate_event,
            'fight': DataValidator.validate_fight
        }
        
        validator = validation_funcs.get(data_type)
        if not validator:
            raise ValidationError(f"Unknown data type: {data_type}")
        
        total = len(data)
        valid = 0
        errors = []
        
        for i, item in enumerate(data):
            try:
                validator(item)
                valid += 1
            except ValidationError as e:
                errors.append(f"Row {i}: {str(e)}")
        
        if errors:
            print(f"Validation warnings for {data_type} data:")
            for error in errors[:10]:  # Muestra solo los primeros 10 errores para evitar saturar la salida
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        return {
            'total': total,
            'valid': valid,
            'invalid': total - valid,
            'success_rate': (valid / total * 100) if total > 0 else 0
        }