import uuid
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.backend.app.database.cosmos_client import PyMongoCosmosDBClient
from app.backend.app.schemas.audit import AuditEvent


def map_method_to_action(method: str) -> str:
    """
    Maps HTTP methods to the FHIR AuditEvent.action codes:
      - C = Create
      - R = Read/View
      - U = Update
      - D = Delete
      - E = Execute (other or custom, e.g. login)

    Args:
        method (str): HTTP method.

    Returns:
        str: FHIR AuditEvent.action code.
    """
    method = method.upper()
    if method == "GET":
        return "R"  # Read
    if method == "POST":
        return "C"  # Create
    if method in ("PUT", "PATCH"):
        return "U"  # Update
    if method == "DELETE":
        return "D"  # Delete
    return "E"  # Execute/other


async def audit_middleware(request: Request, call_next: Callable) -> Response:
    """
    A middleware that logs a FHIR AuditEvent for each request.

    Args:
        request (Request): The FastAPI request.
        call_next (Callable): The FastAPI call_next function.

    Returns:
        Response: The FastAPI response.
    """

    # 1. Capture start time and request details before endpoint runs
    request_time = datetime.now(timezone.utc)
    request_id = str(uuid.uuid4())
    request_method = request.method
    request_url = request.url.path
    client_host = request.client.host
    # NOTE: possible to log other headers: request.headers.get(<key>, <default>)

    # 2. Execute the endpoint (which may set request.state.user_id, etc.)
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        success = 200 <= status_code < 400
    except Exception as exc:
        status_code = 500
        success = False
        response = JSONResponse(content={"detail": str(exc)}, status_code=status_code)

    # 3. After the endpoint, retrieve any data attached via request.state
    user_id = getattr(request.state, "user_id", None)

    # 4. Build the AuditEvent structure
    #    Adjust the content (codes, systems, text) as appropriate for the use case.
    audit_event_dict = {
        "resourceType": "AuditEvent",
        "id": request_id,
        # "meta": { ... },  # Optional if you want to supply FHIR metadata
        #
        # category: High-level type of the event (e.g., "rest", "login", "export")
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/audit-event-type",
                        "code": "rest",  # Example: "rest" for RESTful ops
                        "display": "RESTful Operation",
                    }
                ],
                "text": "RESTful Operation",
            }
        ],
        #
        # code: More specific event type
        "code": {
            "coding": [
                {
                    "system": "http://dicom.nema.org/resources/ontology/DCM",
                    "code": "110100",  # Example: "110100" = Application Activity
                    "display": "Application Activity",
                }
            ],
            "text": "User Login" if request_url == "/login" else "REST API call",
        },
        #
        # action: (C, R, U, D, E)
        "action": map_method_to_action(request_method),
        #
        # severity: e.g., "informational", "warning", "error", etc.
        # The FHIR spec references syslog severity codes.
        # Example: "informational"
        "severity": "informational",
        #
        # occurred[x]: pick either occurredDateTime or occurredPeriod
        # We'll use occurredDateTime to match the "When the activity occurred"
        "occurredDateTime": request_time.isoformat(),
        #
        # recorded: When the event was *recorded* (usually the same as occurredDateTime)
        "recorded": request_time.isoformat(),
        #
        "outcome": {
            # outcome.code is a Coding object that indicates success/failure
            # FHIR R5 suggests "http://terminology.hl7.org/CodeSystem/event-outcome"
            "code": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/event-outcome",
                        "code": "0" if success else "8",
                        "display": "Success" if success else "Failure",
                    }
                ],
                "text": "Operation succeeded" if success else "Operation failed",
            },
            # Additional outcome detail if desired
            # "detail": [
            #     { "text": "Reason for failure..." }
            # ]
        },
        #
        # agent: The actor(s) involved in the event
        # R! - At least one agent is required
        "agent": [
            {
                # "type": { CodeableConcept } if you wish to add a role type
                # "role": [{ CodeableConcept }] if you want to specify roles
                "who": {
                    # Identifies the user or system. If you have a real FHIR resource,
                    # you can reference them. Here we just use an identifier:
                    "identifier": {
                        "value": str(user_id) if user_id is not None else "anonymous"
                    }
                },
                "requestor": True,  # This agent initiated the event
                #
                # We can capture network info (IP, etc.)
                "networkString": client_host,
            }
        ],
        #
        # source: The system or service that recorded/detected the event
        # R! - Required
        "source": {
            # "site" can be a Reference(Location) or just a string
            # "site": {"reference": "Location/1234"} or simple text
            "observer": {
                # Could reference Organization, Device, or Practitioner, etc.
                # For simplicity, just an identifier:
                "identifier": {"value": "My-FastAPI-Application"}
            },
            # The type of source where event originated (CodeableConcept)
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/security-source-type",
                            "code": "4",  # "Application Server"
                            "display": "Application Server",
                        }
                    ],
                    "text": "Application Server",
                }
            ],
        },
        #
        # entity: Any data or objects used. For REST calls, we typically log the URL,
        # or a specific resource reference.
        "entity": [
            {
                "what": {
                    # For a CRUD operation on a FHIR resource, do "Reference(Any)"
                    # e.g., "reference": "Patient/123"
                    # For a more generic call, you might just store the URL
                    "reference": request_url
                },
                "role": {
                    "coding": [
                        {
                            "system": "http://dicom.nema.org/resources/ontology/DCM",
                            "code": "110153",
                            "display": "Source Role ID",
                        }
                    ],
                    "text": "Accessed Resource or Endpoint",
                },
            }
        ],
    }
    audit_event = AuditEvent(**audit_event_dict)

    audit_client: PyMongoCosmosDBClient = request.app.state.audit_client
    # Persist this audit event to Cosmos DB
    await audit_client.get_collection_and_insert_to_collection(audit_event)

    return response
