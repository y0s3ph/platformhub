"""Resource catalog: available infrastructure resources and their parameters."""

from __future__ import annotations

from fastapi import APIRouter

from platformhub.models import ResourceType
from platformhub.schemas import CatalogItem, ParameterSpec

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

CATALOG: list[CatalogItem] = [
    CatalogItem(
        resource_type=ResourceType.K8S_NAMESPACE,
        display_name="Kubernetes Namespace",
        description="Provision a new namespace with resource quotas, network policies, "
        "and RBAC configured for your team.",
        parameters=[
            ParameterSpec(
                name="cpu_limit",
                label="CPU Limit",
                options=["500m", "1", "2", "4"],
                default="1",
                description="Maximum CPU cores for the namespace",
            ),
            ParameterSpec(
                name="memory_limit",
                label="Memory Limit",
                options=["512Mi", "1Gi", "2Gi", "4Gi"],
                default="1Gi",
                description="Maximum memory for the namespace",
            ),
            ParameterSpec(
                name="team",
                label="Team",
                description="Owning team label",
            ),
        ],
    ),
    CatalogItem(
        resource_type=ResourceType.S3_BUCKET,
        display_name="S3 Bucket",
        description="Provision an S3 bucket with encryption, versioning, and "
        "lifecycle policies pre-configured.",
        parameters=[
            ParameterSpec(
                name="versioning",
                label="Enable Versioning",
                type="boolean",
                default="true",
                description="Enable object versioning",
            ),
            ParameterSpec(
                name="region",
                label="AWS Region",
                options=["eu-west-1", "eu-central-1", "us-east-1"],
                default="eu-west-1",
                description="AWS region for the bucket",
            ),
        ],
    ),
    CatalogItem(
        resource_type=ResourceType.RDS_DATABASE,
        display_name="RDS Database",
        description="Provision a managed PostgreSQL database with automated backups, "
        "encryption at rest, and multi-AZ support.",
        parameters=[
            ParameterSpec(
                name="engine_version",
                label="PostgreSQL Version",
                options=["14", "15", "16"],
                default="16",
                description="PostgreSQL engine version",
            ),
            ParameterSpec(
                name="instance_class",
                label="Instance Class",
                options=["db.t3.micro", "db.t3.small", "db.t3.medium"],
                default="db.t3.micro",
                description="RDS instance type",
            ),
            ParameterSpec(
                name="storage_gb",
                label="Storage (GB)",
                type="number",
                default="20",
                description="Allocated storage in GB",
            ),
            ParameterSpec(
                name="multi_az",
                label="Multi-AZ",
                type="boolean",
                default="false",
                description="Enable multi-AZ deployment for high availability",
            ),
        ],
    ),
]


@router.get("/", response_model=list[CatalogItem])
async def list_catalog():
    """List all available infrastructure resources."""
    return CATALOG


@router.get("/{resource_type}", response_model=CatalogItem)
async def get_catalog_item(resource_type: ResourceType):
    """Get details of a specific resource type."""
    for item in CATALOG:
        if item.resource_type == resource_type:
            return item
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Resource type not found")
