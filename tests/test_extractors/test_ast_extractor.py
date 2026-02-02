"""Tests for AST extractor."""

import pytest

from scmextract.extractors.ast_extractor import ASTExtractor
from scmextract.simulators.sir import SIRSimulator


class TestASTExtractor:
    def test_extract_simple_assignment(self):
        """Test extraction from simple variable assignment."""
        code = """
x = a + b
y = x * c
"""
        extractor = ASTExtractor()
        graph = extractor.extract_from_string(code, variables={"x", "y", "a", "b", "c"})
        deps = graph.to_dependencies()

        assert "x" in deps
        assert set(deps["x"]) == {"a", "b"}

        assert "y" in deps
        assert set(deps["y"]) == {"x", "c"}

    def test_extract_with_filter(self):
        """Test that variable filter works."""
        code = """
x = a + b + noise
y = x * c
"""
        extractor = ASTExtractor()
        # Only care about x, y, a, b - not noise or c
        graph = extractor.extract_from_string(code, variables={"x", "y", "a", "b"})
        deps = graph.to_dependencies()

        assert "x" in deps
        assert set(deps["x"]) == {"a", "b"}  # noise filtered out

        assert "y" in deps
        assert set(deps["y"]) == {"x"}  # c filtered out

    def test_extract_list_append(self):
        """Test extraction from list.append() calls."""
        code = """
values = []
values.append(x + y)
"""
        extractor = ASTExtractor()
        graph = extractor.extract_from_string(code, variables={"values", "x", "y"})
        deps = graph.to_dependencies()

        assert "values" in deps
        assert set(deps["values"]) == {"x", "y"}

    def test_extract_attribute_assignment(self):
        """Test extraction from attribute assignment."""
        code = """
self.result = input_a + input_b
"""
        extractor = ASTExtractor()
        graph = extractor.extract_from_string(code, variables={"result", "input_a", "input_b"})
        deps = graph.to_dependencies()

        assert "result" in deps
        assert set(deps["result"]) == {"input_a", "input_b"}

    def test_no_self_reference(self):
        """Test that self-references are excluded."""
        code = """
x = x + 1
"""
        extractor = ASTExtractor()
        graph = extractor.extract_from_string(code, variables={"x"})
        deps = graph.to_dependencies()

        # x = x + 1 should not create x -> x edge
        assert "x" not in deps or "x" not in deps.get("x", [])

    def test_extract_from_sir_simulator(self):
        """Test extraction from actual SIR simulator code."""
        sim = SIRSimulator()
        extractor = ASTExtractor()

        variables = set(sim.get_all_variables())
        graph = extractor.extract(sim.get_source_path(), variables=variables)

        deps = graph.to_dependencies()

        # Should find S_to_I depends on rateSI, Susceptible, Infected
        assert "S_to_I" in deps
        assert "Susceptible" in deps["S_to_I"]
        assert "Infected" in deps["S_to_I"]

        # Should find Susceptible depends on S_to_I
        assert "Susceptible" in deps
        assert "S_to_I" in deps["Susceptible"]


class TestASTExtractorRegistry:
    def test_registered_as_ast(self):
        """Test extractor is registered with name 'ast'."""
        from scmextract.extractors.registry import ExtractorRegistry

        extractor_cls = ExtractorRegistry.get("ast")
        assert extractor_cls == ASTExtractor

    def test_get_extractor_convenience(self):
        """Test get_extractor convenience function."""
        from scmextract.extractors import get_extractor

        extractor = get_extractor("ast")
        assert isinstance(extractor, ASTExtractor)
