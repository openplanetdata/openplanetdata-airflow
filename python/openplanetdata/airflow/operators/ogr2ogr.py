"""Custom Airflow operator for running ogr2ogr inside a GDAL Docker container."""

import os
import shlex

from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from openplanetdata.airflow.defaults import DOCKER_MOUNT

DOCKER_USER = f"{os.getuid()}:{os.getgid()}"


class Ogr2OgrOperator(DockerOperator):
    """Run ogr2ogr inside a GDAL Docker container.

    Args are stored and deferred to execute() so that template_fields rendering
    resolves any XComArg values or Jinja templates before the command is built.
    This allows the operator to be used inside @task_group with expand().
    """

    template_fields = DockerOperator.template_fields + ("args",)

    def __init__(
        self,
        *,
        args: list[str],
        image: str = "ghcr.io/osgeo/gdal:ubuntu-full-latest",
        **kwargs,
    ):
        self.args = args
        kwargs.setdefault("auto_remove", "success")
        kwargs.setdefault("force_pull", True)
        kwargs.setdefault("mount_tmp_dir", False)
        kwargs.setdefault("mounts", [Mount(**DOCKER_MOUNT)])
        kwargs.setdefault("user", DOCKER_USER)
        super().__init__(command="", image=image, **kwargs)

    def execute(self, context):
        cmd = shlex.join(["ogr2ogr", *self.args])
        self.command = f"bash -c {shlex.quote(cmd)}"
        return super().execute(context)
