# Utility functions for BlenderAI addon

def validate_api_key(api_key):
    """Validate API key format."""
    if not api_key or len(api_key) < 10:
        return False
    return True

def format_response(response):
    """Format AI response for display."""
    if isinstance(response, str):
        return response[:500]  # Limit response length
    return str(response)

def log_message(message, level="INFO"):
    """Log messages for debugging."""
    print(f"[{level}] {message}")

def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_message(f"Error: {str(e)}", "ERROR")
        return None
