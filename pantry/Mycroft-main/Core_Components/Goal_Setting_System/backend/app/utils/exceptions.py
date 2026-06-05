"""
Custom exceptions
"""

class GoalExtractionError(Exception):
    """Raised when goal extraction fails"""
    pass

class SimulationError(Exception):
    """Raised when simulation fails"""
    pass

class OllamaConnectionError(Exception):
    """Raised when cannot connect to Ollama"""
    pass

class MarketDataError(Exception):
    """Raised when market data fetch fails"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass