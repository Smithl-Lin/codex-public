# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Unified credential and config loader. All components must use this module
instead of hardcoded API keys or paths. Values are read from environment (.env).
"""
import os
from typing import Optional

# ------------------------------------------------------------------------------
# API Keys (from environment; no defaults to avoid leaking)
# ------------------------------------------------------------------------------
def get_gemini_api_key() -> Optional[str]:
    """Gemini/Google AI API key. Set GEMINI_API_KEY in .env."""
    return os.getenv("GEMINI_API_KEY")


def get_openai_api_key() -> Optional[str]:
    """OpenAI API key. Set OPENAI_API_KEY in .env."""
    return os.getenv("OPENAI_API_KEY")


def get_anthropic_api_key() -> Optional[str]:
    """Anthropic API key. Set ANTHROPIC_API_KEY in .env."""
    return os.getenv("ANTHROPIC_API_KEY")


def get_google_credentials_path() -> Optional[str]:
    """Path to Google service account JSON. Set GOOGLE_APPLICATION_CREDENTIALS in .env."""
    return os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


# ------------------------------------------------------------------------------
# MedGemma / Medical Reasoner (Phase 4)
# ------------------------------------------------------------------------------
def get_medgemma_endpoint() -> Optional[str]:
    """MedGemma or Medical Reasoner endpoint. Set MEDGEMMA_ENDPOINT in .env."""
    return os.getenv("MEDGEMMA_ENDPOINT")


def get_finetune_version() -> str:
    """MedGemma finetune version for prompt template switching. From config or env."""
    return os.getenv("MEDGEMMA_FINETUNE_VERSION", "")
