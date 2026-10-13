"""Descriptor-based Congreve Rule-of-Three fragment screening.

Inputs are supplied molecular descriptors. This module does not calculate them
from SMILES or generate molecular structures.
"""
import math
from typing import Any, Dict


def assess_rule_of_three(molecular_weight: float, clogp: float,
                         hydrogen_bond_donors: int, hydrogen_bond_acceptors: int) -> Dict[str, Any]:
    """Apply the common Ro3 screen: MW <300 Da, cLogP/HBD/HBA <=3."""
    for name, value in (("molecular_weight", molecular_weight), ("clogp", clogp)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
    if molecular_weight <= 0:
        raise ValueError("molecular_weight must be positive")
    for name, value in (("hydrogen_bond_donors", hydrogen_bond_donors),
                        ("hydrogen_bond_acceptors", hydrogen_bond_acceptors)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    checks = {
        "molecular_weight": molecular_weight < 300,
        "clogp": clogp <= 3,
        "hydrogen_bond_donors": hydrogen_bond_donors <= 3,
        "hydrogen_bond_acceptors": hydrogen_bond_acceptors <= 3,
    }
    return {
        "passes": all(checks.values()),
        "criteria": checks,
        "violations": [name for name, passed in checks.items() if not passed],
        "reference": "Congreve et al., Drug Discovery Today (2003), Rule of Three",
        "note": "Heuristic physicochemical filter; not binding, synthesis, safety, or activity prediction.",
    }
