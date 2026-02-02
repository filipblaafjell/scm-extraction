"""Configuration loading utilities."""

from pathlib import Path
from typing import Any, Dict, Union

import yaml

from scmextract.core.types import ExperimentConfig


def load_config(path: Union[str, Path]) -> ExperimentConfig:
    """Load experiment configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        ExperimentConfig instance.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If required fields are missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    return parse_config(data)


def parse_config(data: Dict[str, Any]) -> ExperimentConfig:
    """Parse configuration dictionary into ExperimentConfig.

    Args:
        data: Dictionary with configuration values.

    Returns:
        ExperimentConfig instance.

    Raises:
        ValueError: If required fields are missing.
    """
    required_fields = ['name', 'simulator', 'extractor']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required config field: {field}")

    return ExperimentConfig(
        name=data['name'],
        simulator=data['simulator'],
        extractor=data['extractor'],
        variables=data.get('variables'),
        output_dir=data.get('output_dir', 'results'),
        options=data.get('options', {}),
    )


def save_config(config: ExperimentConfig, path: Union[str, Path]) -> None:
    """Save experiment configuration to a YAML file.

    Args:
        config: ExperimentConfig instance to save.
        path: Path for the output YAML file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'name': config.name,
        'simulator': config.simulator,
        'extractor': config.extractor,
    }

    if config.variables:
        data['variables'] = config.variables
    if config.output_dir != 'results':
        data['output_dir'] = config.output_dir
    if config.options:
        data['options'] = config.options

    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
