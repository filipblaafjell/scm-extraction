"""Simulator registry for discovering and accessing simulators."""

from typing import Dict, Type

from scmextract.core.base import BaseSimulator


class SimulatorRegistry:
    """Registry for simulator classes."""

    _simulators: Dict[str, Type[BaseSimulator]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a simulator class.

        Args:
            name: Unique identifier for the simulator.

        Returns:
            Decorator function.
        """
        def decorator(simulator_cls: Type[BaseSimulator]):
            cls._simulators[name] = simulator_cls
            simulator_cls.name = name
            return simulator_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseSimulator]:
        """Get a simulator class by name.

        Args:
            name: Simulator identifier.

        Returns:
            Simulator class.

        Raises:
            KeyError: If simulator not found.
        """
        if name not in cls._simulators:
            raise KeyError(
                f"Unknown simulator: '{name}'. "
                f"Available: {list(cls._simulators.keys())}"
            )
        return cls._simulators[name]

    @classmethod
    def list_simulators(cls) -> Dict[str, Type[BaseSimulator]]:
        """Return all registered simulators.

        Returns:
            Dictionary mapping names to simulator classes.
        """
        return cls._simulators.copy()


def get_simulator(name: str) -> BaseSimulator:
    """Convenience function to get a simulator instance.

    Args:
        name: Simulator identifier.

    Returns:
        Instantiated simulator.
    """
    return SimulatorRegistry.get(name)()
