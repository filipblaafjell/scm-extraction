"""SCM extraction methods."""

from scmextract.extractors.registry import ExtractorRegistry, get_extractor
from scmextract.extractors.ast_extractor import ASTExtractor

__all__ = [
    "ExtractorRegistry",
    "get_extractor",
    "ASTExtractor",
]
