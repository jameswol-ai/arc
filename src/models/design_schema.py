from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# 🏛️ Core building block of any generated design
@dataclass
class DesignConcept:
    title: str
    description: str
    style_direction: List[str] = field(default_factory=list)
    spatial_idea: str = ""
    climate_strategy: Optional[str] = None


@dataclass
class SiteContext:
    location: Optional[str] = None
    climate_zone: Optional[str] = None
    terrain: Optional[str] = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class MaterialProfile:
    primary_materials: List[str] = field(default_factory=list)
    structural_system: Optional[str] = None
    sustainability_score_hint: Optional[str] = None


@dataclass
class StructuralLogic:
    load_strategy: Optional[str] = None
    foundation_type: Optional[str] = None
    vertical_system: Optional[str] = None
    span_strategy: Optional[str] = None


@dataclass
class ComplianceProfile:
    zoning_rules: List[str] = field(default_factory=list)
    safety_constraints: List[str] = field(default_factory=list)
    accessibility_notes: List[str] = field(default_factory=list)


# 🧠 Full architectural output schema (final assembled “brain output”)
@dataclass
class ArchitecturalDesign:
    project_name: str
    concept: DesignConcept
    site: SiteContext
    materials: MaterialProfile
    structure: StructuralLogic
    compliance: ComplianceProfile
    extra_layers: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "project_name": self.project_name,
            "concept": self.concept.__dict__,
            "site": self.site.__dict__,
            "materials": self.materials.__dict__,
            "structure": self.structure.__dict__,
            "compliance": self.compliance.__dict__,
            "extra_layers": self.extra_layers,
        }
