"""Resource request CRUD endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from platformhub.auth import get_current_user
from platformhub.database import get_db
from platformhub.models import AuditLog, ResourceRequest, User
from platformhub.schemas import ResourceRequestCreate, ResourceRequestResponse

router = APIRouter(prefix="/api/requests", tags=["requests"])


@router.post("/", response_model=ResourceRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: ResourceRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a new infrastructure resource request."""
    resource_request = ResourceRequest(
        resource_type=payload.resource_type,
        name=payload.name,
        environment=payload.environment,
        parameters=json.dumps(payload.parameters),
        requester_id=current_user.id,
    )
    db.add(resource_request)
    await db.flush()

    audit = AuditLog(
        request_id=resource_request.id,
        action="created",
        actor_id=current_user.id,
        details=f"Requested {payload.resource_type.value} '{payload.name}' "
        f"in {payload.environment}",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(resource_request)
    return resource_request


@router.get("/", response_model=list[ResourceRequestResponse])
async def list_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List resource requests. Developers see their own; approvers/admins see all."""
    query = select(ResourceRequest).order_by(ResourceRequest.created_at.desc())
    if current_user.role.value == "developer":
        query = query.where(ResourceRequest.requester_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{request_id}", response_model=ResourceRequestResponse)
async def get_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific resource request by ID."""
    result = await db.execute(select(ResourceRequest).where(ResourceRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if current_user.role.value == "developer" and req.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this request")

    return req


@router.get("/{request_id}/audit")
async def get_request_audit(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit trail for a resource request."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.request_id == request_id)
        .options(selectinload(AuditLog.actor))
        .order_by(AuditLog.created_at)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "action": log.action,
            "actor": log.actor.username,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
