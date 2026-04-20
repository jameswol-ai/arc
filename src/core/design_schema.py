from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DesignConcept:
    title: str
    description: str
    climate_strategy: str
    materials: List[str]


@dataclass
class ComplianceReport:
    passed: bool
    issues: List[str] = field(default_factory=list)
    standards_checked: List[str] = field(default_factory=list)


@dataclass
class FinalDesign:
    concept: DesignConcept
    compliance: ComplianceReport
    drawings: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class WorkflowResult:
    success: bool
    design: FinalDesign
    metadata: Dict[str, Any] = field(default_factory=dict)
