"""Pipelines for the linter."""

from .argument_pipeline import ArgumentPipeline
from .base import BasePipeline
from .discovery_pipeline import DiscoveryPipeline
from .validation_pipeline import ValidationPipeline

__all__ = [
    "ArgumentPipeline",
    "BasePipeline",
    "DiscoveryPipeline",
    "ValidationPipeline",
]
