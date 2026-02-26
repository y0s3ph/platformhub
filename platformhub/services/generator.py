"""Manifest generator using Jinja2 templates."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from platformhub.models import ResourceRequest, ResourceType

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "manifests"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def generate_manifest(request: ResourceRequest) -> str:
    """Render the infrastructure manifest for an approved request."""
    template_map = {
        ResourceType.K8S_NAMESPACE: "k8s_namespace.yaml.j2",
        ResourceType.S3_BUCKET: "s3_bucket.tf.j2",
        ResourceType.RDS_DATABASE: "rds_database.tf.j2",
    }

    template_name = template_map.get(request.resource_type)
    if not template_name:
        return f"# No template available for {request.resource_type.value}"

    template = _env.get_template(template_name)
    params = json.loads(request.parameters) if request.parameters else {}

    return template.render(
        name=request.name,
        environment=request.environment,
        params=params,
    )
