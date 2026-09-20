from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class InvestigationRequest(BaseModel):
    # Defaults are None now. Before, a missing box silently became Elena.
    name: Optional[str] = None
    username: Optional[str] = None
    context: Optional[str] = None
    image_base64: Optional[str] = None
    consent_acknowledged: bool = True

class SignalBreakdown(BaseModel):
    name_similarity: float
    username_similarity: float
    org_similarity: float
    project_similarity: float
    semantic_similarity: float
    photo_hash_similarity: float
    composite_confidence: float
    signals_matched: List[str]

class CandidateMatch(BaseModel):
    id: str
    name: str
    primary_handle: str
    headline: str
    location: str
    avatar_url: str
    confidence: float
    status: str
    is_selected: bool
    signals: SignalBreakdown
    selection_reasons: List[str]
    rejection_reasons: List[str]

class ProfileRecord(BaseModel):
    id: str
    platform: str
    handle: str
    url: str
    bio: str
    followers: Optional[str] = "12.4k"
    verified: bool = True
    confidence: float
    status: str
    signals_matched: List[str]
    avatar_url: Optional[str] = None

class EntityResolutionData(BaseModel):
    canonical_name: str
    aliases: List[str]
    handles: List[str]
    primary_domains: List[str]
    disambiguation_summary: str
    alias_clusters: List[Dict[str, Any]]

class ExtractedEntities(BaseModel):
    people: List[Dict[str, str]]
    organizations: List[Dict[str, str]]
    roles: List[Dict[str, str]]
    projects: List[Dict[str, str]]
    events: List[Dict[str, str]]
    publications: List[Dict[str, str]]
    technologies: List[str]
    patents_products: List[Dict[str, str]]

class CorrelationItem(BaseModel):
    id: str
    signal_name: str
    indicator: str
    platforms: List[str]
    correlation_strength: str
    explanation: str

class EvidenceItem(BaseModel):
    id: str
    claim: str
    source: str
    source_platform: str
    evidence_snippet: str
    confidence: float
    status: str
    corroboration_count: int

class TimelineEvent(BaseModel):
    id: str
    date: str
    year: int
    title: str
    platform: str
    category: str
    description: str
    evidence_id: Optional[str] = None

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    weight: float = 1.0

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class ConflictRecord(BaseModel):
    candidate_id: str
    name: str
    domain: str
    similarity_score: float
    decision: str
    conflict_type: str
    conflict_details: str
    why_not_merged: str

class InvestigationResult(BaseModel):
    query: InvestigationRequest
    candidates: List[CandidateMatch]
    selected_candidate: CandidateMatch
    profiles: List[ProfileRecord]
    entity_resolution: EntityResolutionData
    extracted_entities: ExtractedEntities
    correlations: List[CorrelationItem]
    evidence_ledger: List[EvidenceItem]
    timeline: List[TimelineEvent]
    graph: GraphData
    conflicts: List[ConflictRecord]
    privacy_notice: str