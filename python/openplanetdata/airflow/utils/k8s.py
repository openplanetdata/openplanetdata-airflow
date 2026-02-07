"""
Kubernetes utilities for Airflow task configuration.
"""

from __future__ import annotations

from kubernetes.client import models as k8s

# Default worker image
DEFAULT_WORKER_IMAGE = "ghcr.io/openplanetdata/airflow:latest"


def create_pod_spec(
    memory_request: str = "2Gi",
    memory_limit: str = "4Gi",
    cpu_request: str = "1",
    cpu_limit: str = "2",
    image: str | None = None,
    env_vars: dict[str, str] | None = None,
) -> dict:
    """
    Create executor_config with pod_override for KubernetesExecutor.

    Args:
        memory_request: Memory request (e.g., "2Gi")
        memory_limit: Memory limit (e.g., "4Gi")
        cpu_request: CPU request (e.g., "1")
        cpu_limit: CPU limit (e.g., "2")
        image: Container image (defaults to DEFAULT_WORKER_IMAGE)
        env_vars: Additional environment variables

    Returns:
        executor_config dict for use with @task decorator

    Example:
        @task(executor_config=create_pod_spec(memory_limit="8Gi"))
        def my_task():
            ...
    """
    container_env = [
        k8s.V1EnvVar(name="OGR_GEOJSON_MAX_OBJ_SIZE", value="0"),
    ]

    if env_vars:
        for name, value in env_vars.items():
            container_env.append(k8s.V1EnvVar(name=name, value=str(value)))

    return {
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                        image=image or DEFAULT_WORKER_IMAGE,
                        resources=k8s.V1ResourceRequirements(
                            requests={"memory": memory_request, "cpu": cpu_request},
                            limits={"memory": memory_limit, "cpu": cpu_limit},
                        ),
                        env=container_env,
                    )
                ]
            )
        )
    }


# Pre-defined pod configurations for common workloads
POD_SMALL = create_pod_spec(
    memory_request="512Mi",
    memory_limit="1Gi",
    cpu_request="250m",
    cpu_limit="500m",
)

POD_DEFAULT = create_pod_spec(
    memory_request="1Gi",
    memory_limit="2Gi",
    cpu_request="500m",
    cpu_limit="1",
)

POD_MEDIUM = create_pod_spec(
    memory_request="2Gi",
    memory_limit="4Gi",
    cpu_request="1",
    cpu_limit="2",
)

POD_LARGE = create_pod_spec(
    memory_request="4Gi",
    memory_limit="8Gi",
    cpu_request="2",
    cpu_limit="4",
)

POD_XLARGE = create_pod_spec(
    memory_request="8Gi",
    memory_limit="16Gi",
    cpu_request="2",
    cpu_limit="4",
)
