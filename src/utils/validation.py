"""Data validation utilities."""
from typing import Dict, Any, List, Optional
from ..core.exceptions import ValidationError


class DataValidator:
    """Validates scraped data integrity."""
    
    @staticmethod
    def validate_fighter(fighter: Dict[str, Any]) -> bool:
        """Validate fighter data."""
        required_fields = ['fighter_id']
        
        for field in required_fields:
            if not fighter.get(field):
                raise ValidationError(f"Fighter missing required field: {field}")
        
        # At least name components should exist
        has_name = (fighter.get('first') and fighter.get('last')) or fighter.get('name')
        if not has_name:
            raise ValidationError(f"Fighter {fighter['fighter_id']} missing name information")
        
        return True
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> bool:
        """Validate event data."""
        required_fields = ['event_id', 'name']
        
        for field in required_fields:
            if not event.get(field):
                raise ValidationError(f"Event missing required field: {field}")
        
        return True
    
    @staticmethod
    def validate_fight(fight: Dict[str, Any]) -> bool:
        """Validate fight data."""
        required_fields = ['event_id', 'fight_id']
        
        for field in required_fields:
            if not fight.get(field):
                raise ValidationError(f"Fight missing required field: {field}")
        
        return True
    
    @staticmethod
    def validate_dataset(data: List[Dict[str, Any]], data_type: str) -> Dict[str, int]:
        """Validate entire dataset."""
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
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        return {
            'total': total,
            'valid': valid,
            'invalid': total - valid,
            'success_rate': (valid / total * 100) if total > 0 else 0
        }