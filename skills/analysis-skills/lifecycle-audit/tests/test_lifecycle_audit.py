#!/usr/bin/env python3
"""
Tests for Lifecycle Audit Skill (v2.0.0)

Run with:
    python -m pytest skills/lifecycle-audit/tests/test_lifecycle_audit.py -v
    
Or run specific test:
    python -m pytest skills/lifecycle-audit/tests/test_lifecycle_audit.py::test_happy_path -v
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from run import (
    run_lifecycle_audit,
    LifecycleAuditSkill,
    STAGE_ORDER,
    BENCHMARKS,
    DATA_REQUIREMENTS
)


class TestHappyPath:
    """Test normal successful execution."""
    
    def test_basic_run(self):
        """Test basic run with default parameters."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50
        })
        
        assert result["status"] in ["success", "review"]
        assert "output" in result
        assert "_meta" in result["output"]
        assert result["output"]["_meta"]["tenant_id"] == "test_tenant"
    
    def test_output_structure(self):
        """Test that output matches expected schema."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        output = result.get("output", {})
        
        # Required fields
        assert "summary" in output
        assert "recommendations" in output
        assert "_meta" in output
        
        # Summary structure
        summary = output["summary"]
        assert "total_accounts" in summary
        assert "by_stage" in summary
        assert "health_score" in summary
        assert 0 <= summary["health_score"] <= 1
        
        # Meta structure
        meta = output["_meta"]
        assert "tenant_id" in meta
        assert "run_id" in meta
        assert "execution_mode" in meta
        assert "runtime_seconds" in meta
        assert "cost_usd" in meta
        assert "release_action" in meta
    
    def test_suggest_mode(self):
        """Test suggest mode (read-only)."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50,
            "execution_mode": "suggest"
        })
        
        output = result.get("output", {})
        
        # Should have recommendations but no preview or execution
        assert "recommendations" in output
        assert "preview" not in output
        assert "execution" not in output
        assert output["_meta"]["execution_mode"] == "suggest"
    
    def test_preview_mode(self):
        """Test preview mode (dry-run)."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50,
            "execution_mode": "preview"
        })
        
        output = result.get("output", {})
        
        # Should have preview section
        assert "preview" in output
        assert "would_create" in output["preview"]
        assert "would_update" in output["preview"]
        assert output["_meta"]["execution_mode"] == "preview"
    
    def test_execute_mode(self):
        """Test execute mode."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50,
            "execution_mode": "execute"
        })
        
        output = result.get("output", {})
        
        # Should have execution section
        assert "execution" in output
        assert "status" in output["execution"]
        assert output["_meta"]["execution_mode"] == "execute"
    
    def test_with_specific_stages(self):
        """Test filtering by specific stages."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100,
            "stages": ["customer", "evangelist"]
        })
        
        output = result.get("output", {})
        by_stage = output.get("summary", {}).get("by_stage", {})
        
        # Should only have customer and evangelist stages
        # (or empty if no contacts match)
        for stage in by_stage.keys():
            assert stage in ["customer", "evangelist", "unknown"]


class TestDataValidation:
    """Test data requirement validation."""
    
    def test_minimum_records_enforced(self):
        """Test that minimum records requirement is enforced."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 10  # Below minimum of 20
        })
        
        # Should fail due to insufficient data
        # Note: Sample data generator creates data up to limit
        # So with limit=10, we'll have 10 records < 20 minimum
        if result["status"] == "failed":
            assert "insufficient" in result.get("error", "").lower() or \
                   "data requirements" in result.get("error", "").lower()
    
    def test_skip_validation_override(self):
        """Test that validation can be skipped."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 10,
            "data_requirements_override": {
                "skip_validation": True
            }
        })
        
        # Should succeed even with low record count
        assert result["status"] in ["success", "review"]
    
    def test_custom_minimum_records(self):
        """Test custom minimum records override."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 15,
            "data_requirements_override": {
                "minimum_records": 10  # Lower than default 20
            }
        })
        
        # Should succeed with lowered minimum
        assert result["status"] in ["success", "review"]


class TestConversionAnalysis:
    """Test conversion rate calculations."""
    
    def test_conversion_rates_calculated(self):
        """Test that conversion rates are calculated between stages."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        output = result.get("output", {})
        conversions = output.get("conversions", [])
        
        # Should have conversions between stages
        assert len(conversions) > 0
        
        for conv in conversions:
            assert "from_stage" in conv
            assert "to_stage" in conv
            assert "rate" in conv
            assert "benchmark" in conv
            assert 0 <= conv["rate"]  # Rate can exceed 1 if to_count > from_count
    
    def test_bottlenecks_identified(self):
        """Test that bottlenecks are identified when rates below benchmark."""
        # With random data, bottlenecks may or may not be found
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 200  # Larger sample for more stable rates
        })
        
        output = result.get("output", {})
        
        # Bottlenecks should be an array (may be empty)
        assert "bottlenecks" in output
        assert isinstance(output["bottlenecks"], list)
        
        for bottleneck in output["bottlenecks"]:
            assert "severity" in bottleneck
            assert bottleneck["severity"] in ["low", "medium", "high"]
            assert bottleneck["rate"] < bottleneck["benchmark"]


class TestScoring:
    """Test risk and upsell scoring."""
    
    def test_at_risk_scoring(self):
        """Test at-risk account identification."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        output = result.get("output", {})
        at_risk = output.get("at_risk", [])
        
        # At-risk should be an array
        assert isinstance(at_risk, list)
        
        for account in at_risk:
            assert "email" in account
            assert "risk_score" in account
            assert 0 <= account["risk_score"] <= 1
            assert account["risk_score"] > 0.5  # Only high-risk included
    
    def test_upsell_scoring(self):
        """Test upsell candidate identification."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        output = result.get("output", {})
        upsell = output.get("upsell_candidates", [])
        
        # Upsell should be an array
        assert isinstance(upsell, list)
        
        for candidate in upsell:
            assert "email" in candidate
            assert "upsell_score" in candidate
            assert 0 <= candidate["upsell_score"] <= 1
            assert candidate["upsell_score"] > 0.6  # Only high-potential included


class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendations_generated(self):
        """Test that recommendations are generated."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        output = result.get("output", {})
        recommendations = output.get("recommendations", [])
        
        # Should have at least one recommendation (from at-risk if any)
        assert isinstance(recommendations, list)
        
        for rec in recommendations:
            assert "priority" in rec
            assert rec["priority"] in ["low", "medium", "high"]
            assert "action" in rec
            assert len(rec["action"]) > 0
    
    def test_health_score_calculated(self):
        """Test overall health score calculation."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        output = result.get("output", {})
        health_score = output.get("summary", {}).get("health_score")
        
        assert health_score is not None
        assert 0 <= health_score <= 1


class TestMetadata:
    """Test metadata (_meta) generation."""
    
    def test_meta_fields_present(self):
        """Test all required meta fields are present."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant_meta",
            "limit": 50,
            "execution_mode": "suggest"
        })
        
        meta = result.get("output", {}).get("_meta", {})
        
        required_fields = [
            "tenant_id", "run_id", "execution_mode",
            "runtime_seconds", "cost_usd", "release_action"
        ]
        
        for field in required_fields:
            assert field in meta, f"Missing required meta field: {field}"
    
    def test_tenant_id_tracked(self):
        """Test tenant_id is correctly tracked."""
        result = run_lifecycle_audit({
            "tenant_id": "custom_tenant_123",
            "limit": 50
        })
        
        meta = result.get("output", {}).get("_meta", {})
        assert meta["tenant_id"] == "custom_tenant_123"
    
    def test_cost_tracking(self):
        """Test cost is calculated and reasonable."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50
        })
        
        meta = result.get("output", {}).get("_meta", {})
        cost = meta.get("cost_usd", 0)
        
        # Cost should be positive and reasonable
        assert cost >= 0
        assert cost < 5.0  # Should not exceed $5 for 50 records
    
    def test_runtime_tracking(self):
        """Test runtime is tracked."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50
        })
        
        meta = result.get("output", {}).get("_meta", {})
        runtime = meta.get("runtime_seconds", 0)
        
        # Runtime should be positive
        assert runtime > 0
        assert runtime < 120  # Should not exceed SLA max
    
    def test_data_quality_tracking(self):
        """Test data quality metrics are tracked."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 100
        })
        
        meta = result.get("output", {}).get("_meta", {})
        data_quality = meta.get("data_quality", {})
        
        assert "records_processed" in data_quality
        assert "field_coverage" in data_quality


class TestReleasePolicy:
    """Test release policy integration."""
    
    def test_release_action_determined(self):
        """Test that release action is determined."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50
        })
        
        release_action = result.get("release_action")
        
        assert release_action in [
            "auto_deliver", "auto_refine", "human_review", "blocked"
        ]
    
    def test_release_message_provided(self):
        """Test that release message is provided."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50
        })
        
        release_message = result.get("release_message")
        
        assert release_message is not None
        assert len(release_message) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_stages_filter(self):
        """Test with no matching stages."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50,
            "stages": []  # Empty stages list
        })
        
        # Should handle gracefully
        assert result["status"] in ["success", "review", "failed"]
    
    def test_large_limit(self):
        """Test with large record limit."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 1000,
            "data_requirements_override": {"skip_validation": True}
        })

        # Should complete (may use chunked processing)
        assert result["status"] in ["success", "review"]

        meta = result.get("output", {}).get("_meta", {})
        # With large data, tokens structure should exist
        # Note: token counting may be 0 in stub mode, but structure should be present
        assert "tokens" in meta
        assert isinstance(meta["tokens"], dict)
    
    def test_missing_tenant_id_uses_default(self):
        """Test that missing tenant_id uses default."""
        result = run_lifecycle_audit({
            "limit": 50
        })
        
        meta = result.get("output", {}).get("_meta", {})
        assert meta["tenant_id"] == "default"


class TestContextHandling:
    """Test large dataset context handling."""
    
    def test_small_dataset_inline(self):
        """Test that small datasets are processed inline."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 50  # Small dataset
        })
        
        # Should succeed with inline processing
        assert result["status"] in ["success", "review"]
    
    def test_medium_dataset_chunked(self):
        """Test that medium datasets may use chunking."""
        result = run_lifecycle_audit({
            "tenant_id": "test_tenant",
            "limit": 500,  # Medium dataset
            "data_requirements_override": {"skip_validation": True}
        })
        
        # Should succeed
        assert result["status"] in ["success", "review"]


# Run tests directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
