"""Custom Airflow operator for running gol inside the OpenPlanetData Docker container."""

import os
import shlex

from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from openplanetdata.airflow.defaults import DOCKER_MOUNT, OPENPLANETDATA_IMAGE

DOCKER_USER = f"{os.getuid()}:{os.getgid()}"


class GolOperator(DockerOperator):
    """Run gol inside the OpenPlanetData Docker container.

    Args are stored and deferred to execute() so that template_fields rendering
    resolves any XComArg values or Jinja templates before the command is built.
    This allows the operator to be used inside @task_group with expand().
    """

    template_fields = DockerOperator.template_fields + ("args", "output_file")

    def __init__(
        self,
        *,
        args: list[str],
        output_file: str | None = None,
        image: str = OPENPLANETDATA_IMAGE,
        **kwargs,
    ):
        self.args = args
        self.output_file = output_file
        kwargs.setdefault("auto_remove", "success")
        kwargs.setdefault("force_pull", True)
        kwargs.setdefault("mount_tmp_dir", False)
        kwargs.setdefault("mounts", [Mount(**DOCKER_MOUNT)])
        kwargs.setdefault("user", DOCKER_USER)
        super().__init__(command="", image=image, **kwargs)

    def execute(self, context):
        cmd = shlex.join(["gol", *self.args])
        if self.output_file:
            cmd = f"{cmd} > {self.output_file}"
        self.command = f"bash -c {shlex.quote(cmd)}"
        return super().execute(context)
