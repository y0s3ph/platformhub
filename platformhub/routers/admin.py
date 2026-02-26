"""Admin/approver endpoints for reviewing resource requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from platformhub.auth import require_role
from platformhub.database import get_db
from platformhub.models import RequestStatus, ResourceRequest, Role, User
from platformhub.schemas import ResourceRequestResponse, ReviewAction
from platformhub.services.approval import review_request

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/pending", response_model=list[ResourceRequestResponse])
async def list_pending_requests(
    _current_user: User = Depends(require_role(Role.APPROVER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all pending resource requests awaiting review."""
    result = await db.execute(
        select(ResourceRequest)
        .where(ResourceRequest.status == RequestStatus.PENDING)
        .order_by(ResourceRequest.created_at)
    )
    return result.scalars().all()


@router.post("/{request_id}/review", response_model=ResourceRequestResponse)
async def review(
    request_id: int,
    payload: ReviewAction,
    current_user: User = Depends(require_role(Role.APPROVER, Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a resource request. Generates manifests on approval."""
    result = await db.execute(
        select(ResourceRequest).where(ResourceRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    try:
        updated = await review_request(req, current_user, payload.action, payload.comment, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return updated
