from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    operational_driver = "operational_driver"
    resource_load = "resource_load"
    human_factor = "human_factor"
    risk = "risk"
    outcome = "outcome"
    business_outcome = "business_outcome"
    cost_driver = "cost_driver"
    financial_outcome = "financial_outcome"
    decision = "decision"
    sales_outcome = "sales_outcome"
    capacity_driver = "capacity_driver"
    supply_driver = "supply_driver"


class Polarity(str, Enum):
    positive = "positive"
    negative = "negative"
    mixed = "mixed"


class WillowNode(BaseModel):
    id: str
    label: str
    type: NodeType
    unit: str
    current_value: float
    confidence: float = Field(ge=0.0, le=1.0)
    description: str


class WillowEdge(BaseModel):
    id: str
    source: str
    target: str
    polarity: Polarity
    weight: float = Field(ge=0.0, le=1.0)
    lag: str
    rationale: str


class WillowGraph(BaseModel):
    graph_id: str
    name: str
    domain: str
    version: str
    nodes: List[WillowNode]
    edges: List[WillowEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Intervention(BaseModel):
    node_id: str
    operation: Literal["set", "increase_by", "decrease_by", "multiply_by"]
    value: float
    reason: Optional[str] = None


class SimulationOptions(BaseModel):
    propagation_depth: int = Field(default=4, ge=1, le=12)
    include_counterfactuals: bool = True
    include_fragility: bool = True
    include_recommendations: bool = True
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class WillowSimulationRequest(BaseModel):
    simulation_id: str
    graph_id: str
    scenario_name: str
    context: Dict[str, Any] = Field(default_factory=dict)
    baseline: Dict[str, float]
    interventions: List[Intervention]
    simulation_options: SimulationOptions = Field(default_factory=SimulationOptions)


class WillowSimulationResponse(BaseModel):
    simulation_id: str
    scenario_name: str
    projected_values: Dict[str, float]
    projected_changes: List[Dict[str, Any]]


class DecisionLedgerItem(BaseModel):
    decision_id: str
    decision_type: str
    entity_type: str
    entity_id: Optional[str] = None
    title: str
    recommendation: str
    chosen_action: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    expected_value: Optional[float] = None
    risk_score: Optional[float] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    assumptions: List[Dict[str, Any]] = Field(default_factory=list)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)


class ReverseEngineerRequest(BaseModel):
    entity_type: str
    entity_id: str
    decision_id: Optional[str] = None
    predicted: Dict[str, float]
    actual: Dict[str, float]
    context: Dict[str, Any] = Field(default_factory=dict)
