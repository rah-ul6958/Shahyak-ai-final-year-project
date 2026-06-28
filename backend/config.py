"""
SAHAYAK-AI Configuration Module

Handles hardware profile detection and provides model configurations
for different hardware capabilities.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import psutil
from pydantic import Field
from pydantic_settings import BaseSettings


class HardwareProfile(str, Enum):
    """Hardware profile enumeration for resource-based configuration."""

    LOW = "low"
    MID = "mid"
    HIGH = "high"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Hardware configuration
    hardware_profile: HardwareProfile = Field(
        default=HardwareProfile.MID,
        description="Hardware profile: low, mid, or high"
    )

    # Ollama configuration
    ollama_host: str = Field(
        default="http://ollama:11434",
        description="Ollama service host"
    )
    ollama_model: str = Field(
        default="llama3:8b-q4",
        description="Ollama model name"
    )

    # ChromaDB configuration
    chroma_path: Path = Field(
        default=Path("./data/chroma_db"),
        description="ChromaDB persistent storage path"
    )

    # OSRM configuration
    osrm_host: str = Field(
        default="http://osrm:5000",
        description="OSRM routing service host"
    )

    # Whisper configuration
    whisper_model: str = Field(
        default="base",
        description="Whisper model size: tiny, base, small"
    )

    # Model cache directories
    embed_cache_dir: Path = Field(
        default=Path("./data/models/embeddings"),
        description="FastEmbed model cache directory"
    )
    reranker_cache_dir: Path = Field(
        default=Path("./data/models/reranker"),
        description="Cross-encoder reranker cache directory"
    )
    whisper_cache_dir: Path = Field(
        default=Path("./data/models/whisper"),
        description="Whisper model cache directory"
    )

    # API configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API host address"
    )
    api_port: int = Field(
        default=8000,
        description="API port"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Model configuration per hardware profile
MODEL_CONFIG: Dict[HardwareProfile, Dict[str, str]] = {
    HardwareProfile.LOW: {
        "model": "gemma2:2b",
        "whisper": "tiny",
        "embed_batch": "16",
    },
    HardwareProfile.MID: {
        "model": "llama3:8b-q4",
        "whisper": "base",
        "embed_batch": "32",
    },
    HardwareProfile.HIGH: {
        "model": "llama3:8b",
        "whisper": "small",
        "embed_batch": "64",
    },
}


def detect_profile() -> HardwareProfile:
    """
    Detect hardware profile based on available RAM.

    Returns:
        HardwareProfile: The detected hardware profile
    """
    # Check environment variable first
    profile = os.getenv("HARDWARE_PROFILE")
    if profile:
        try:
            return HardwareProfile(profile.lower())
        except ValueError:
            pass

    # Auto-detect based on RAM
    ram_gb = psutil.virtual_memory().total / (1024**3)

    if ram_gb >= 28:
        return HardwareProfile.HIGH
    elif ram_gb >= 14:
        return HardwareProfile.MID
    return HardwareProfile.LOW


def get_settings() -> Settings:
    """
    Get application settings with auto-detection of hardware profile.

    Returns:
        Settings: Configured application settings
    """
    profile = detect_profile()
    model_cfg = MODEL_CONFIG[profile]

    return Settings(
        hardware_profile=profile,
        ollama_model=model_cfg["model"],
        whisper_model=model_cfg["whisper"],
    )


def get_model_config(profile: Optional[HardwareProfile] = None) -> Dict[str, str]:
    """
    Get model configuration for a hardware profile.

    Args:
        profile: Hardware profile to get config for. If None, uses auto-detection.

    Returns:
        Dict containing model configuration
    """
    if profile is None:
        profile = detect_profile()
    return MODEL_CONFIG.get(profile, MODEL_CONFIG[HardwareProfile.MID])


# Global settings instance
settings = get_settings()