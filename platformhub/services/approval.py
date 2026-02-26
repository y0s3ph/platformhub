"""Approval workflow service."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from platformhub.models import AuditLog, RequestStatus, ResourceRequest, User
from platformhub.services.generator import generate_manifest


async def review_request(
    request: ResourceRequest,
    reviewer: User,
    action: RequestStatus,
    comment: str,
    db: AsyncSession,
) -> ResourceRequest:
    """Approve or reject a resource request."""
    if request.status != RequestStatus.PENDING:
        msg = f"Request is already {request.status.value}"
        raise ValueError(msg)

    if action not in (RequestStatus.APPROVED, RequestStatus.REJECTED):
        msg = "Action must be 'approved' or 'rejected'"
        raise ValueError(msg)

    request.status = action
    request.reviewer_id = reviewer.id
    request.review_comment = comment
    request.reviewed_at = datetime.now(tz=UTC)

    if action == RequestStatus.APPROVED:
        request.generated_manifest = generate_manifest(request)

    audit = AuditLog(
        request_id=request.id,
        action=action.value,
        actor_id=reviewer.id,
        details=comment or f"Request {action.value} by {reviewer.username}",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(request)
    return request
