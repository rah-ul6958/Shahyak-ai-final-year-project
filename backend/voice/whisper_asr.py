"""
SAHAYAK-AI Whisper ASR

OpenAI Whisper for offline speech-to-text transcription.
"""

import os
import tempfile
from typing import Optional

import structlog
import whisper

from config import settings

logger = structlog.get_logger(__name__)

# Whisper model sizes
WHISPER_SIZES = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "large": "large",
}


class WhisperASR:
    """
    Whisper-based offline speech-to-text.
    """

    def __init__(
        self,
        model_size: str = "base",
        download_root: Optional[str] = None,
    ):
        """
        Initialize Whisper ASR.

        Args:
            model_size: Model size (tiny, base, small, medium, large)
            download_root: Directory to cache downloaded models
        """
        self.model_size = model_size
        self.download_root = download_root or str(settings.whisper_cache_dir)
        self._model = None

        # Create cache directory
        os.makedirs(self.download_root, exist_ok=True)

    @property
    def model(self) -> whisper.Whisper:
        """Lazy-load Whisper model."""
        if self._model is None:
            logger.info("loading_whisper_model", model_size=self.model_size)
            self._model = whisper.load_model(
                self.model_size,
                download_root=self.download_root,
            )
            logger.info("whisper_model_loaded")
        return self._model

    def transcribe(
        self,
        audio_path: str,
        language: str = "en",
        fp16: bool = False,
    ) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file
            language: Language code (default: English)
            fp16: Use FP16 (set to False for CPU)

        Returns:
            Transcribed text
        """
        logger.info("transcribing_audio", audio_path=audio_path, language=language)

        result = self.model.transcribe(
            audio_path,
            language=language,
            fp16=fp16,
        )

        text = result["text"].strip()
        logger.info(
            "transcription_complete",
            text_length=len(text),
            language=result.get("language"),
        )

        return text

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        language: str = "en",
        fp16: bool = False,
    ) -> str:
        """
        Transcribe audio from bytes.

        Args:
            audio_bytes: Audio file bytes
            language: Language code
            fp16: Use FP16

        Returns:
            Transcribed text
        """
        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            return self.transcribe(temp_path, language, fp16)
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning("temp_file_cleanup_failed", error=str(e))


# Global Whisper ASR instance
_whisper_asr: Optional[WhisperASR] = None


def get_whisper_asr(
    model_size: Optional[str] = None,
) -> WhisperASR:
    """
    Get global Whisper ASR instance.

    Args:
        model_size: Model size (defaults to settings)

    Returns:
        WhisperASR instance
    """
    global _whisper_asr

    if _whisper_asr is None:
        size = model_size or settings.whisper_model
        _whisper_asr = WhisperASR(
            model_size=size,
        )

    return _whisper_asr


def transcribe_audio(
    audio_path: str,
    language: str = "en",
) -> str:
    """
    Convenience function to transcribe audio file.

    Args:
        audio_path: Path to audio file
        language: Language code

    Returns:
        Transcribed text
    """
    asr = get_whisper_asr()
    return asr.transcribe(audio_path, language)