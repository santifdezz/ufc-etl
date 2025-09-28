"""
Excepciones personalizadas para el scraper de UFC.
Define una jerarquía de errores específicos para el proceso de scraping, parsing, validación y configuración.
Permite un manejo más preciso y profesional de los errores en el pipeline ETL.
"""


class UFCScraperError(Exception):
    """
    Excepción base para todos los errores del scraper de UFC.
    Todas las excepciones personalizadas deben heredar de esta clase.
    """
    pass


class ScrapingError(UFCScraperError):
    """
    Se lanza cuando ocurre un fallo durante el proceso de scraping de datos.
    """
    pass


class ParsingError(UFCScraperError):
    """
    Se lanza cuando ocurre un error al parsear datos extraídos.
    """
    pass


class ValidationError(UFCScraperError):
    """
    Se lanza cuando la validación de datos falla.
    Permite identificar registros o estructuras inválidas en el flujo ETL.
    """
    pass


class ConfigurationError(UFCScraperError):
    """
    Se lanza cuando la configuración del sistema es inválida o está incompleta.
    """
    pass