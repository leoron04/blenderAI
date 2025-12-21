"""Configuration management for BlenderAI addon.

Provides easy API configuration, model selection with recommendations,
and AUTO mode for intelligent model selection.
"""

import os
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class AIModel(Enum):
    """Available AI models with metadata."""
    
    CHATGPT_4 = "gpt-4"
    CHATGPT_35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    LOCAL_LLAMA = "llama-2-7b"
    AUTO = "auto"


@dataclass
class ModelInfo:
    """Information about an AI model."""
    
    id: str
    name: str
    provider: str
    speed: str  # "Fast", "Medium", "Slow"
    quality: str  # 1-5 stars
    cost: str  # "Free", "Low", "High"
    context_window: int
    supports_vision: bool = False
    supports_code: bool = True
    recommended_for: List[str] = None
    icon: str = "bot"
    
    def __post_init__(self):
        if self.recommended_for is None:
            self.recommended_for = []


# Comprehensive model information database
MODEL_INFO: Dict[str, ModelInfo] = {
    "gpt-4": ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="OpenAI",
        speed="Medium",
        quality="5 stars",
        cost="High",
        context_window=8000,
        supports_vision=True,
        icon="brain",
        recommended_for=["Complex scenes", "Advanced modeling", "Code generation"]
    ),
    "gpt-3.5-turbo": ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider="OpenAI",
        speed="Fast",
        quality="4 stars",
        cost="Low",
        context_window=4000,
        supports_vision=False,
        icon="lightning",
        recommended_for=["Quick edits", "Simple tasks", "Budget-friendly"]
    ),
    "claude-3-opus": ModelInfo(
        id="claude-3-opus",
        name="Claude 3 Opus",
        provider="Anthropic",
        speed="Medium",
        quality="5 stars",
        cost="High",
        context_window=200000,
        supports_vision=True,
        icon="palette",
        recommended_for=["Large projects", "Detailed scenes", "Long context"]
    ),
    "claude-3-sonnet": ModelInfo(
        id="claude-3-sonnet",
        name="Claude 3 Sonnet",
        provider="Anthropic",
        speed="Fast",
        quality="4 stars",
        cost="Medium",
        context_window=200000,
        supports_vision=True,
        icon="music",
        recommended_for=["Balanced tasks", "Good quality", "Reasonable cost"]
    ),
    "gemini-pro": ModelInfo(
        id="gemini-pro",
        name="Gemini Pro",
        provider="Google",
        speed="Fast",
        quality="4 stars",
        cost="Medium",
        context_window=30000,
        supports_vision=False,
        icon="sparkles",
        recommended_for=["Scene analysis", "Material creation", "Optimization"]
    ),
    "llama-2-7b": ModelInfo(
        id="llama-2-7b",
        name="Llama 2 7B (Local)",
        provider="Meta (Local)",
        speed="Fast",
        quality="3 stars",
        cost="Free",
        context_window=4000,
        supports_vision=False,
        icon="robot",
        recommended_for=["Privacy", "Offline use", "Local processing"]
    ),
}


class APIConfig:
    """Easy API configuration for BlenderAI."""
    
    def __init__(self):
        """Initialize API configuration from environment or defaults."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.selected_model = os.getenv("BLENDER_AI_MODEL", "auto")
        self.auto_mode_enabled = os.getenv("BLENDER_AI_AUTO_MODE", "true").lower() == "true"
    
    def set_openai_key(self, api_key: str) -> bool:
        """Set OpenAI API key."""
        if not api_key or len(api_key) < 20:
            return False
        self.openai_api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        return True
    
    def set_anthropic_key(self, api_key: str) -> bool:
        """Set Anthropic API key."""
        if not api_key or len(api_key) < 20:
            return False
        self.anthropic_api_key = api_key
        os.environ["ANTHROPIC_API_KEY"] = api_key
        return True
    
    def set_google_key(self, api_key: str) -> bool:
        """Set Google API key."""
        if not api_key or len(api_key) < 20:
            return False
        self.google_api_key = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        return True
    
    def get_available_models(self) -> List[Tuple[str, str]]:
        """Get list of models with available API keys.
        
        Returns:
            List of (model_id, model_name) tuples for models with configured API keys.
        """
        available = []
        
        if self.openai_api_key:
            available.append(("gpt-4", "GPT-4"))
            available.append(("gpt-3.5-turbo", "GPT-3.5 Turbo"))
        
        if self.anthropic_api_key:
            available.append(("claude-3-opus", "Claude 3 Opus"))
            available.append(("claude-3-sonnet", "Claude 3 Sonnet"))
        
        if self.google_api_key:
            available.append(("gemini-pro", "Gemini Pro"))
        
        # Local models are always available
        available.append(("llama-2-7b", "Llama 2 (Local)"))
        available.append(("auto", "Auto Select (Recommended)"))
        
        return available
    
    def select_best_model(self, task_type: str = "general") -> str:
        """Intelligently select best model for task.
        
        Args:
            task_type: "complex", "fast", "vision", "coding", or "general"
        
        Returns:
            Selected model ID.
        """
        available = {m[0]: m[0] for m in self.get_available_models()}
        
        # Remove 'auto' from available for selection
        available.pop("auto", None)
        
        if not available:
            return "llama-2-7b"
        
        # Task-specific recommendations
        if task_type == "complex":
            if "gpt-4" in available:
                return "gpt-4"
            if "claude-3-opus" in available:
                return "claude-3-opus"
            if "gpt-3.5-turbo" in available:
                return "gpt-3.5-turbo"
        
        elif task_type == "fast":
            if "gpt-3.5-turbo" in available:
                return "gpt-3.5-turbo"
            if "gemini-pro" in available:
                return "gemini-pro"
            if "claude-3-sonnet" in available:
                return "claude-3-sonnet"
        
        elif task_type == "vision":
            if "gpt-4" in available:
                return "gpt-4"
            if "claude-3-opus" in available:
                return "claude-3-opus"
            if "claude-3-sonnet" in available:
                return "claude-3-sonnet"
        
        elif task_type == "coding":
            if "gpt-4" in available:
                return "gpt-4"
            if "claude-3-opus" in available:
                return "claude-3-opus"
            if "gpt-3.5-turbo" in available:
                return "gpt-3.5-turbo"
        
        quality_order = [
            "gpt-4",
            "claude-3-opus",
            "claude-3-sonnet",
            "gpt-3.5-turbo",
            "gemini-pro",
            "llama-2-7b"
        ]
        
        for model in quality_order:
            if model in available:
                return model
        
        return list(available.keys())[0]
    
    def is_configured(self) -> bool:
        """Check if at least one API is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key or self.google_api_key)


# Global configuration instance
api_config = APIConfig()


def get_model_info(model_id: str) -> Optional[ModelInfo]:
    """Get detailed information about a model.
    
    Args:
        model_id: Model identifier
    
    Returns:
        ModelInfo object or None if not found.
    """
    return MODEL_INFO.get(model_id)


def get_recommended_model() -> str:
    """Get recommended model for current project.
    
    Returns:
        Model ID of recommended model.
    """
    return api_config.select_best_model("general")
