"""SCM Extract - Extract Structural Causal Models from simulator code."""

from scmextract.core.types import CausalGraph, ExperimentConfig
from scmextract.core.base import BaseSimulator, BaseExtractor
from scmextract.extractors.ast_extractor import ASTExtractor
from scmextract.simulators.sir import SIRSimulator

__version__ = "0.1.0"

__all__ = [
    "CausalGraph",
    "ExperimentConfig",
    "BaseSimulator",
    "BaseExtractor",
    "ASTExtractor",
    "SIRSimulator",
]
