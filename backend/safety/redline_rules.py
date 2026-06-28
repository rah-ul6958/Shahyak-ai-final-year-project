"""
SAHAYAK-AI Redline Rules

Deterministic hard-rule contraindication engine for dangerous instructions.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RedlineResult:
    """Result of redline check."""

    triggered: bool
    matched_rules: List[str]
    safe_instructions: List[str]


# Redline rules for dangerous instructions
# Each rule has:
# - pattern: regex to match dangerous instruction
# - override: safe replacement instruction
# - hazard: hazard type this rule applies to
REDLINE_RULES: List[Dict[str, str]] = [
    # Fire - Electrical
    {
        "pattern": r"use water.{0,30}(electrical|electric|live wire)",
        "override": "DO NOT use water on electrical fires. Use a CO₂ or dry powder extinguisher only. If unavailable, evacuate the area and call emergency services.",
        "hazard": "FIRE",
    },
    {
        "pattern": r"throw water.{0,30}(electrical|electric)",
        "override": "DO NOT throw water on electrical fires. Use a CO₂ extinguisher or evacuate.",
        "hazard": "FIRE",
    },
    {
        "pattern": r"extinguish.{0,30}(electrical|electric).{0,10}water",
        "override": "DO NOT use water on electrical fires. Use appropriate fire extinguisher.",
        "hazard": "FIRE",
    },
    # Fire - General dangerous
    {
        "pattern": r"use gasoline.{0,30}fire",
        "override": "DO NOT use gasoline or flammable liquids on fires. Evacuate and use appropriate extinguisher.",
        "hazard": "FIRE",
    },
    {
        "pattern": r"run through.{0,20}fire",
        "override": "DO NOT run through fire. evacuate immediately using the safest exit route.",
        "hazard": "FIRE",
    },
    # Medical - Spinal injuries
    {
        "pattern": r"move.{0,30}(spinal|spine|neck|back) injur",
        "override": "DO NOT move a person with a suspected spinal injury. Keep them still in the position found, support the head and neck, and await professional medical help.",
        "hazard": "MEDICAL",
    },
    {
        "pattern": r"turn over.{0,30}(injured|patient)",
        "override": "DO NOT turn over an injured person unless they are in immediate danger. Moving may worsen spinal injuries.",
        "hazard": "MEDICAL",
    },
    {
        "pattern": r"walk.{0,20}(back injury|spinal)",
        "override": "Person with suspected back/spinal injury should not walk. Keep them still.",
        "hazard": "MEDICAL",
    },
    # Medical - Bleeding
    {
        "pattern": r"remove.{0,20}(embedded|impaled).{0,10}object",
        "override": "DO NOT remove embedded or impaled objects. Stabilize them in place and seek medical help.",
        "hazard": "MEDICAL",
    },
    {
        "pattern": r"apply tourniquet.{0,20}without",
        "override": "Only apply a tourniquet as a last resort for life-threatening bleeding. Improper use can cause tissue damage.",
        "hazard": "MEDICAL",
    },
    # Earthquake - Building collapse
    {
        "pattern": r"re-?enter.{0,30}(collapsed|damaged|structurally)",
        "override": "DO NOT re-enter a structurally compromised building. Move to the designated muster point and await safety clearance.",
        "hazard": "EARTHQUAKE",
    },
    {
        "pattern": r"go back.{0,30}building",
        "override": "DO NOT go back into any building after an earthquake until declared safe.",
        "hazard": "EARTHQUAKE",
    },
    {
        "pattern": r"enter.{0,30}(cracked|broken).{0,10}building",
        "override": "DO NOT enter buildings showing signs of structural damage. Report to assembly point.",
        "hazard": "EARTHQUAKE",
    },
    # Flood
    {
        "pattern": r"walk through.{0,20}flooded.{0,20}water",
        "override": "DO NOT walk through flooded water. Currents can be stronger than they appear. Seek higher ground.",
        "hazard": "FLOOD",
    },
    {
        "pattern": r"drive through.{0,20}flood",
        "override": "DO NOT drive through flooded roads. Turn around and find an alternate route. Just 6 inches of water can sweep you off your feet.",
        "hazard": "FLOOD",
    },
    {
        "pattern": r"swim.{0,20}flood",
        "override": "DO NOT try to swim in flood water. It may contain hazards. Get to higher ground.",
        "hazard": "FLOOD",
    },
    # Chemical
    {
        "pattern": r"inhale.{0,20}chemical",
        "override": "DO NOT inhale chemicals. Move to fresh air immediately. Cover nose and mouth.",
        "hazard": "CHEMICAL",
    },
    {
        "pattern": r"touch.{0,20}chemical.{0,20}without",
        "override": "DO NOT touch hazardous materials without proper protective equipment. Evacuate the area.",
        "hazard": "CHEMICAL",
    },
    # Cyclone
    {
        "pattern": r"go outside.{0,20}cyclone",
        "override": "DO NOT go outside during a cyclone. Stay indoors in a safe room away from windows.",
        "hazard": "CYCLONE",
    },
    {
        "pattern": r"watch.{0,20}storm.{0,20}outside",
        "override": "DO NOT go outside to watch the storm. Stay indoors for safety.",
        "hazard": "CYCLONE",
    },
]


def check_redlines(
    instructions: List[str],
    hazard_type: str,
) -> RedlineResult:
    """
    Check instructions against redline rules.

    Args:
        instructions: List of generated instructions
        hazard_type: Hazard type for context

    Returns:
        RedlineResult with triggered status and safe instructions
    """
    matched_rules = []
    safe_instructions = []

    for instruction in instructions:
        instruction_lower = instruction.lower()
        triggered = False

        for rule in REDLINE_RULES:
            # Check if rule applies to current hazard type
            # MEDICAL rules apply to all hazards; others only to their specific hazard
            if rule["hazard"] != hazard_type and rule["hazard"] != "MEDICAL":
                continue

            # Check pattern
            pattern = rule["pattern"]
            if re.search(pattern, instruction_lower, re.IGNORECASE):
                matched_rules.append(f"{rule['hazard']}: {rule['override'][:50]}...")
                safe_instructions.append(rule["override"])
                triggered = True
                logger.warning(
                    "redline_triggered",
                    hazard_type=hazard_type,
                    original_instruction=instruction[:100],
                    override=rule["override"][:50],
                )
                break

        if not triggered:
            safe_instructions.append(instruction)

    return RedlineResult(
        triggered=len(matched_rules) > 0,
        matched_rules=matched_rules,
        safe_instructions=safe_instructions,
    )


def get_all_rules() -> List[Dict[str, str]]:
    """
    Get all redline rules.

    Returns:
        List of rule dicts
    """
    return REDLINE_RULES.copy()


def add_rule(
    pattern: str,
    override: str,
    hazard: str,
) -> None:
    """
    Add a new redline rule.

    Args:
        pattern: Regex pattern to match
        override: Safe override text
        hazard: Hazard type
    """
    REDLINE_RULES.append({
        "pattern": pattern,
        "override": override,
        "hazard": hazard,
    })

    logger.info("redline_rule_added", hazard=hazard, pattern=pattern[:50])