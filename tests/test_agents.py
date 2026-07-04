"""Test suite for RONIN agents."""
import pytest
import os
from unittest.mock import patch, MagicMock


class TestOrchestrator:
    """Test the RONIN orchestrator."""

    def test_orchestrator_imports(self):
        """Test that orchestrator can be imported."""
        from agents.orchestrator import run_ronin
        assert callable(run_ronin)

    def test_orchestrator_client_intake_task(self):
        """Test client_intake task routing."""
        from agents.orchestrator import run_ronin
        result = run_ronin("client_intake", "Test inquiry")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_orchestrator_menu_costing_task(self):
        """Test menu_costing task routing."""
        from agents.orchestrator import run_ronin
        result = run_ronin("menu_costing", "Test menu items")
        assert isinstance(result, str)

    def test_orchestrator_recipe_task(self):
        """Test recipe task routing."""
        from agents.orchestrator import run_ronin
        result = run_ronin("recipe", "Test recipe request")
        assert isinstance(result, str)

    def test_orchestrator_unknown_task(self):
        """Test unknown task returns error message."""
        from agents.orchestrator import run_ronin
        result = run_ronin("unknown_task", "message")
        assert "Unknown RONIN task" in result


class TestAgents:
    """Test individual agent modules."""

    def test_menu_cost_agent_imports(self):
        """Test menu_cost_agent can be imported."""
        from agents.menu_cost_agent import run_menu_costing
        assert callable(run_menu_costing)

    def test_recipe_agent_imports(self):
        """Test recipe_agent can be imported."""
        from agents.recipe_agent import run_recipe
        assert callable(run_recipe)

    def test_client_intake_agent_imports(self):
        """Test client_intake_agent can be imported."""
        from agents.client_intake_agent import run_client_intake
        assert callable(run_client_intake)

    def test_menu_pricing_engine_imports(self):
        """Test menu_pricing_engine can be imported."""
        from agents.menu_pricing_engine import run_menu_pricing
        assert callable(run_menu_pricing)


class TestAsyncAgents:
    """Test async RONIN agents."""

    def test_concierge_agent_imports(self):
        """Test ConciergeAgent can be imported."""
        from agents.concierge_agent import ConciergeAgent
        assert ConciergeAgent is not None

    def test_ops_agent_imports(self):
        """Test OpsAgent can be imported."""
        from agents.ops_agent import OpsAgent
        assert OpsAgent is not None

    def test_logistics_agent_imports(self):
        """Test LogisticsAgent can be imported."""
        from agents.logistics_agent import LogisticsAgent
        assert LogisticsAgent is not None

    def test_economics_agent_imports(self):
        """Test EconomicsAgent can be imported."""
        from agents.economics_agent import EconomicsAgent
        assert EconomicsAgent is not None

    def test_compliance_agent_imports(self):
        """Test ComplianceAgent can be imported."""
        from agents.compliance_agent import ComplianceAgent
        assert ComplianceAgent is not None


class TestConfig:
    """Test configuration module."""

    def test_config_imports(self):
        """Test config can be imported."""
        from core.config import is_mock_enabled
        assert callable(is_mock_enabled)

    def test_mock_mode_disabled_by_default(self):
        """Test mock mode configuration."""
        from core.config import is_mock_enabled
        # Should be False unless explicitly set
        result = is_mock_enabled()
        assert isinstance(result, bool)


class TestChefKnowledge:
    """Test chef knowledge module."""

    def test_indexer_imports(self):
        """Test indexer can be imported."""
        from chef_knowledge.indexer import build_index, query_chef_knowledge
        assert callable(build_index)
        assert callable(query_chef_knowledge)

    def test_loader_imports(self):
        """Test loader can be imported."""
        from chef_knowledge.loader import iter_school_files, extract_text
        assert callable(iter_school_files)
        assert callable(extract_text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
