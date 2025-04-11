from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Coding(BaseModel):
    system: str
    code: str
    display: str


class CodeableConcept(BaseModel):
    coding: list[Coding]
    text: str | None = None


class Identifier(BaseModel):
    value: str


class Who(BaseModel):
    """
    Minimal structure for 'who', which in FHIR can be a Reference or an Identifier, etc.
    Here, we've simplified it to just an Identifier with a 'value'.
    """

    identifier: Identifier


class Agent(BaseModel):
    who: Who
    requestor: bool
    networkString: str | None = None


class OutcomeDetail(BaseModel):
    text: str


class Outcome(BaseModel):
    code: CodeableConcept
    detail: list[OutcomeDetail] | None = None


class Observer(BaseModel):
    """
    Minimal structure for 'observer'.
    """

    identifier: Identifier


class Source(BaseModel):
    observer: Observer
    type: list[CodeableConcept]
    # site could be added here if needed


class EntityWhat(BaseModel):
    """
    Minimal structure for the 'what' field in an entity.
    """

    reference: str


class Entity(BaseModel):
    what: EntityWhat
    role: CodeableConcept


class AuditEvent(BaseModel):
    resourceType: Literal["AuditEvent"] = Field(
        "AuditEvent", description="Should always be 'AuditEvent'"
    )
    id: str
    # meta: Optional[dict] = None  # If you want to handle FHIR's meta object

    category: list[CodeableConcept]
    code: CodeableConcept
    action: str
    severity: str
    occurredDateTime: datetime
    recorded: datetime
    outcome: Outcome

    agent: list[Agent]
    source: Source
    entity: list[Entity]
