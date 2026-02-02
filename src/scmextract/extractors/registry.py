"""Extractor registry for discovering and accessing extraction methods."""

from typing import Dict, Type

from scmextract.core.base import BaseExtractor


class ExtractorRegistry:
    """Registry for extractor classes."""

    _extractors: Dict[str, Type[BaseExtractor]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register an extractor class.

        Args:
            name: Unique identifier for the extractor.

        Returns:
            Decorator function.
        """
        def decorator(extractor_cls: Type[BaseExtractor]):
            cls._extractors[name] = extractor_cls
            extractor_cls.name = name
            return extractor_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseExtractor]:
        """Get an extractor class by name.

        Args:
            name: Extractor identifier.

        Returns:
            Extractor class.

        Raises:
            KeyError: If extractor not found.
        """
        if name not in cls._extractors:
            raise KeyError(
                f"Unknown extractor: '{name}'. "
                f"Available: {list(cls._extractors.keys())}"
            )
        return cls._extractors[name]

    @classmethod
    def list_extractors(cls) -> Dict[str, Type[BaseExtractor]]:
        """Return all registered extractors.

        Returns:
            Dictionary mapping names to extractor classes.
        """
        return cls._extractors.copy()


def get_extractor(name: str) -> BaseExtractor:
    """Convenience function to get an extractor instance.

    Args:
        name: Extractor identifier.

    Returns:
        Instantiated extractor.
    """
    return ExtractorRegistry.get(name)()
