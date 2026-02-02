"""AST-based causal graph extraction from Python source code."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set

from scmextract.core.base import BaseExtractor
from scmextract.core.types import CausalGraph
from scmextract.extractors.registry import ExtractorRegistry


class CausalASTVisitor(ast.NodeVisitor):
    """AST visitor that extracts causal dependencies between variables."""

    def __init__(self, variables_of_interest: Optional[Set[str]] = None):
        self.dependencies: Dict[str, List[str]] = {}
        self.variables_of_interest = variables_of_interest

    def _get_referenced_names(self, node: ast.AST) -> List[str]:
        """Extract all variable names referenced in an expression."""
        names = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.append(child.id)
            elif isinstance(child, ast.Attribute):
                names.append(child.attr)

        if self.variables_of_interest:
            names = [n for n in names if n in self.variables_of_interest]
        return list(set(names))

    def _add_dependency(self, target: str, deps: List[str]) -> None:
        """Add dependencies for a target variable."""
        deps = [d for d in deps if d != target]  # Remove self-reference
        if not deps:
            return
        if target in self.dependencies:
            self.dependencies[target] = list(set(self.dependencies[target] + deps))
        else:
            self.dependencies[target] = deps

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle: X = expression"""
        target = node.targets[0]
        if isinstance(target, ast.Name):
            target_name = target.id
        elif isinstance(target, ast.Attribute):
            target_name = target.attr
        else:
            self.generic_visit(node)
            return

        if self.variables_of_interest and target_name not in self.variables_of_interest:
            self.generic_visit(node)
            return

        deps = self._get_referenced_names(node.value)
        self._add_dependency(target_name, deps)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Handle: X.append(expression) and similar mutations."""
        if isinstance(node.func, ast.Attribute) and node.func.attr == "append":
            if isinstance(node.func.value, ast.Name):
                target_name = node.func.value.id
                if self.variables_of_interest is None or target_name in self.variables_of_interest:
                    deps = self._get_referenced_names(node.args[0]) if node.args else []
                    self._add_dependency(target_name, deps)
        self.generic_visit(node)


@ExtractorRegistry.register("ast")
class ASTExtractor(BaseExtractor):
    """Extract causal graphs from Python source using AST parsing.

    This extractor analyzes Python source code to identify causal
    relationships by tracking variable assignments and mutations.
    """

    def extract(self, source_path: Path, variables: Optional[Set[str]] = None) -> CausalGraph:
        """Extract causal graph from a Python source file.

        Args:
            source_path: Path to the Python file.
            variables: Optional set of variables to focus on.

        Returns:
            CausalGraph with extracted dependencies.
        """
        source_path = Path(source_path)
        with open(source_path, "r") as f:
            source_code = f.read()

        return self.extract_from_string(source_code, variables)

    def extract_from_string(self, source_code: str, variables: Optional[Set[str]] = None) -> CausalGraph:
        """Extract causal graph from Python source code string.

        Args:
            source_code: Python source code.
            variables: Optional set of variables to focus on.

        Returns:
            CausalGraph with extracted dependencies.
        """
        tree = ast.parse(source_code)
        visitor = CausalASTVisitor(variables_of_interest=variables)
        visitor.visit(tree)

        var_list = sorted(variables) if variables else None
        return CausalGraph.from_dependencies(visitor.dependencies, variables=var_list)
