"""Custom exceptions for UFC scraper."""


class UFCScraperError(Exception):
    """Base exception for UFC scraper."""
    pass


class ScrapingError(UFCScraperError):
    """Raised when scraping fails."""
    pass


class ParsingError(UFCScraperError):
    """Raised when parsing fails."""
    pass


class ValidationError(UFCScraperError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(UFCScraperError):
    """Raised when configuration is invalid."""
    pass