# Adding New Extractors

This guide explains how to add new causal graph extraction methods to SCM Extract.

## Overview

Extractors analyze source code to identify causal relationships between variables. The framework supports multiple extraction methods through a registry pattern.

## Step-by-step

### 1. Create a new extractor file

Create a new file in `src/scmextract/extractors/`:

```python
# src/scmextract/extractors/my_extractor.py

from pathlib import Path
from typing import Optional, Set

from scmextract.core.base import BaseExtractor
from scmextract.core.types import CausalGraph
from scmextract.extractors.registry import ExtractorRegistry


@ExtractorRegistry.register("my_method")
class MyExtractor(BaseExtractor):
    """My custom extraction method.

    Describe what your method does and its approach.
    """

    def extract(self, source_path: Path, variables: Optional[Set[str]] = None) -> CausalGraph:
        """Extract causal graph from source code.

        Args:
            source_path: Path to the Python source file.
            variables: Optional set of variables to focus on.

        Returns:
            CausalGraph with extracted dependencies.
        """
        # Read source code
        with open(source_path, "r") as f:
            source_code = f.read()

        # Your extraction logic here
        dependencies = self._analyze(source_code, variables)

        # Convert to CausalGraph
        var_list = sorted(variables) if variables else None
        return CausalGraph.from_dependencies(dependencies, variables=var_list)

    def _analyze(self, source_code: str, variables: Optional[Set[str]]) -> dict:
        """Analyze source code and return dependencies dict."""
        # Implement your analysis logic
        # Return dict like: {"Y": ["X"], "Z": ["Y", "X"]}
        pass
```

### 2. Register the extractor

The `@ExtractorRegistry.register("my_method")` decorator automatically registers your extractor. The string argument becomes the name used in the CLI.

### 3. Update the package imports

Add your extractor to `src/scmextract/extractors/__init__.py`:

```python
from scmextract.extractors.my_extractor import MyExtractor

__all__ = [
    # ... existing exports
    "MyExtractor",
]
```

### 4. Write tests

Create tests in `tests/test_extractors/test_my_extractor.py`:

```python
import pytest
from scmextract.extractors.my_extractor import MyExtractor


class TestMyExtractor:
    def test_simple_extraction(self):
        code = """
x = a + b
y = x * 2
"""
        extractor = MyExtractor()
        graph = extractor.extract_from_string(code, variables={"x", "y", "a", "b"})
        deps = graph.to_dependencies()

        assert "x" in deps
        assert set(deps["x"]) == {"a", "b"}

    def test_registered(self):
        from scmextract.extractors import get_extractor
        extractor = get_extractor("my_method")
        assert isinstance(extractor, MyExtractor)
```

### 5. Use your extractor

Via CLI:
```bash
scmextract extract model.py --method my_method
scmextract benchmark --methods ast my_method
```

Via Python:
```python
from scmextract.extractors import get_extractor

extractor = get_extractor("my_method")
graph = extractor.extract(source_path, variables={"X", "Y"})
```

## Best Practices

1. **Filter by variables**: Respect the `variables` parameter to focus extraction on relevant variables only.

2. **Handle edge cases**: Return empty graphs gracefully when no dependencies are found.

3. **Document assumptions**: Clearly document what patterns your extractor recognizes and its limitations.

4. **Support `extract_from_string`**: Implement this method if your extractor can work with source code strings (useful for testing).

## Example: LLM-based Extractor

Here's a sketch for an LLM-based extractor:

```python
@ExtractorRegistry.register("llm")
class LLMExtractor(BaseExtractor):
    """Extract causal graphs using an LLM."""

    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def extract(self, source_path: Path, variables: Optional[Set[str]] = None) -> CausalGraph:
        with open(source_path, "r") as f:
            source_code = f.read()

        prompt = self._build_prompt(source_code, variables)
        response = self._call_llm(prompt)
        dependencies = self._parse_response(response)

        return CausalGraph.from_dependencies(dependencies, variables=sorted(variables))

    def _build_prompt(self, source_code: str, variables: Set[str]) -> str:
        return f"""Analyze this Python code and identify causal dependencies between variables.

Variables of interest: {variables}

Code:
```python
{source_code}
```

Return a JSON object mapping each variable to its direct causes.
"""
```

## Existing Extractors

| Name | Class | Description |
|------|-------|-------------|
| `ast` | `ASTExtractor` | Static analysis using Python's AST module |
