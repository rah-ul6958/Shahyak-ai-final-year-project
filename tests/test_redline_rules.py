"""
SAHAYAK-AI Redline Rules Tests

Tests for the deterministic contraindication engine.
"""

import sys
from pathlib import Path

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestRedlineRules:
    """Tests for redline rule checking."""

    def test_fire_electrical_water_rule(self):
        """Test FIRE rule: water on electrical fire."""
        from safety.redline_rules import check_redlines

        instructions = ["Use water on the electrical fire to extinguish it."]
        result = check_redlines(instructions, "FIRE")

        assert result.triggered is True
        assert len(result.matched_rules) > 0
        assert len(result.safe_instructions) == 1
        assert "DO NOT" in result.safe_instructions[0]

    def test_medical_spinal_injury_rule(self):
        """Test MEDICAL rule: moving spinal injury patient."""
        from safety.redline_rules import check_redlines

        instructions = ["Move the person with spinal injury to safety."]
        result = check_redlines(instructions, "MEDICAL")

        assert result.triggered is True
        assert "DO NOT" in result.safe_instructions[0]

    def test_earthquake_reentry_rule(self):
        """Test EARTHQUAKE rule: re-entering damaged building."""
        from safety.redline_rules import check_redlines

        instructions = ["Re-enter the collapsed building to retrieve documents."]
        result = check_redlines(instructions, "EARTHQUAKE")

        assert result.triggered is True
        assert "DO NOT" in result.safe_instructions[0]

    def test_flood_driving_rule(self):
        """Test FLOOD rule: driving through flood."""
        from safety.redline_rules import check_redlines

        instructions = ["Drive through the flooded road to reach safety."]
        result = check_redlines(instructions, "FLOOD")

        assert result.triggered is True
        assert "DO NOT" in result.safe_instructions[0]

    def test_cyclone_outdoor_rule(self):
        """Test CYCLONE rule: going outside during cyclone."""
        from safety.redline_rules import check_redlines

        instructions = ["Go outside to watch the cyclone storm."]
        result = check_redlines(instructions, "CYCLONE")

        assert result.triggered is True
        assert "DO NOT" in result.safe_instructions[0]

    def test_safe_instruction_passes(self):
        """Test that safe instructions pass redline check."""
        from safety.redline_rules import check_redlines

        instructions = [
            "Move to higher ground immediately.",
            "Do not attempt to cross flooded roads.",
            "Listen to emergency broadcasts.",
        ]
        result = check_redlines(instructions, "FLOOD")

        assert result.triggered is False
        assert len(result.safe_instructions) == 3

    def test_medical_rules_apply_to_all_hazards(self):
        """Test that MEDICAL rules apply regardless of hazard type."""
        from safety.redline_rules import check_redlines

        # This should trigger even for FIRE hazard
        instructions = ["Move the person with spinal injury."]
        result = check_redlines(instructions, "FIRE")

        assert result.triggered is True

    def test_hazard_specific_rules_dont_cross(self):
        """Test that FIRE rules don't trigger for FLOOD instructions."""
        from safety.redline_rules import check_redlines

        instructions = ["Use a fire extinguisher on the flames."]
        result = check_redlines(instructions, "FLOOD")

        # Should not trigger FIRE-specific rules for FLOOD hazard
        assert result.triggered is False

    def test_multiple_instructions_mixed(self):
        """Test redline check with mix of safe and dangerous instructions."""
        from safety.redline_rules import check_redlines

        instructions = [
            "Move to higher ground immediately.",
            "Use water on the electrical fire.",
            "Call emergency services.",
        ]
        result = check_redlines(instructions, "FIRE")

        assert result.triggered is True
        # First and third should be kept, second should be replaced
        assert len(result.safe_instructions) == 3
        assert "higher ground" in result.safe_instructions[0]
        assert "DO NOT" in result.safe_instructions[1]
        assert "emergency services" in result.safe_instructions[2]

    def test_case_insensitive_matching(self):
        """Test that pattern matching is case insensitive."""
        from safety.redline_rules import check_redlines

        instructions = ["USE WATER ON THE ELECTRICAL FIRE"]
        result = check_redlines(instructions, "FIRE")

        assert result.triggered is True

    def test_get_all_rules(self):
        """Test getting all redline rules."""
        from safety.redline_rules import get_all_rules

        rules = get_all_rules()

        assert len(rules) >= 15  # At least 15 rules as per spec
        assert all("pattern" in rule for rule in rules)
        assert all("override" in rule for rule in rules)
        assert all("hazard" in rule for rule in rules)

    def test_add_new_rule(self):
        """Test adding a new redline rule."""
        from safety.redline_rules import add_rule, get_all_rules

        initial_count = len(get_all_rules())

        add_rule(
            pattern=r"test pattern",
            override="Test override",
            hazard="TEST",
        )

        new_count = len(get_all_rules())
        assert new_count == initial_count + 1
