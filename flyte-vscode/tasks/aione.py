from dataclasses import dataclass

from flytekit import PodTemplate, Resources, task, workflow
from kubernetes.client.models import V1PodSpec, V1Container, V1EnvVar, V1ResourceRequirements, V1Toleration, V1Volume, V1VolumeMount, V1EmptyDirVolumeSource, V1Secret, V1PersistentVolumeClaimVolumeSource
from flytekitplugins.flyteinteractive import vscode


@dataclass
class GitData:
    repo_url: str
    target_dir: str
    access_token: str
    branch: str


@dataclass
class S3Data:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    bucket_path: str
    target_dir: str


@dataclass
class WorkflowInputs:
    codes: list[GitData]
    s3datas: list[S3Data]
    command: str
    ssh: str

command = """"""
command_list = ["/bin/sh", "-c", command] if command else None

pod_template=PodTemplate(
    primary_container_name="aione-main-container",
    labels={"aione_id":"ins-0e4d65d4ijfw0a6817t9268ue2"},
    annotations={"aione_owner":"ljgong", "aione_tenant": "opo-01jx96xy3c485hj04rgva7w64j"},
    pod_spec= V1PodSpec(
        init_containers=[
            V1Container(
                name="aione-download-container",
                image="docker.fzyun.io/founder/aione.download:1.0.0.51",
                env=[V1EnvVar(name="AIONE_PARAMS",value="eyJsaWJJRCI6IDIsICJkb2NJZCI6IDE4LCAibmFtZSI6ICJcdTViOThcdTY1YjlJREUyIiwgImRlc2NyaXB0aW9uIjogIiIsICJpZCI6ICJpbnMtMGU0ZDY1ZDRpamZ3MGE2ODE3dDkyNjh1ZTIiLCAicnVuU3RhdHVzIjogMywgIm9zc0RhdGFzIjogW10sICJwcm9qZWN0SWQiOiAicG1wLTAxanllMzJqeXA2cDBlZmI5YTE4eHI1Z25mIiwgIm93bmVyIjogImxqZ29uZyIsICJhdXRob3IiOiAibGpnb25nIiwgIm9wZXJhdG9yIjogImxqZ29uZyIsICJ0ZW5hbnQiOiAib3BvLTAxang5Nnh5M2M0ODVoajA0cmd2YTd3NjRqIiwgImNyZWF0ZWQiOiAiMjAyNS0wOC0wNlQxODoyMzoyMC4wMDBaIiwgImxhc3RNb2RpZmllZCI6ICIyMDI1LTA4LTA3VDE3OjQwOjI0LjAwMFoiLCAicmVzVHlwZSI6ICJDMk00IiwgImltYWdlVHlwZSI6ICJPV04iLCAiaW1hZ2UiOiAicmVnaXN0cnktdGNlbnRlci0wMDEuZGM0LWZhYXMuZnp5dW4uaW8vZm91bmRlci9haW9uZS5pZGU6MS4wLjAuNTQtZGV2IiwgImltYWdlS2V5IjogImxqZ29uZyIsICJpbWFnZVNlY3JldCI6ICJGb3VuZGVyMTIzIiwgInJ1blBpcGVsaW5lIjogImFkd3M3azdnN2hqMnNnbjJwNDloIiwgInJ1blRpbWUiOiAiMjAyNS0wOC0wN1QxNzo0MDo1MS4wMDBaIiwgInJ1blRpbWVFbmQiOiAiMjAyNS0wOC0wN1QxNzo0Mjo1MS4wMDBaIiwgInJ1bkVycm9yIjogIlRyYWNlOlxuXG4gICAgVHJhY2ViYWNrIChtb3N0IHJlY2VudCBjYWxsIGxhc3QpOlxuICAgICAgRmlsZSBcIi91c3IvbG9jYWwvbGliL3B5dGhvbjMuMTIvZGlzdC1wYWNrYWdlcy9mbHl0ZWtpdC9jb3JlL2Jhc2VfdGFzay5weVwiLCBsaW5lIDc2NywgaW4gZGlzcGF0Y2hfZXhlY3V0ZVxuICAgICAgICBuYXRpdmVfb3V0cHV0cyA9IHNlbGYuZXhlY3V0ZSgqKm5hdGl2ZV9pbnB1dHMpXG4gICAgICAgICAgICAgICAgICAgICAgICAgXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5cbiAgICAgIEZpbGUgXCIvdXNyL2xvY2FsL2xpYi9weXRob24zLjEyL2Rpc3QtcGFja2FnZXMvZmx5dGVraXQvY29yZS9weXRob25fZnVuY3Rpb25fdGFzay5weVwiLCBsaW5lIDIxNCwgaW4gZXhlY3V0ZVxuICAgICAgICByZXR1cm4gc2VsZi5fdGFza19mdW5jdGlvbigqKmt3YXJncylcbiAgICAgICAgICAgICAgIF5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXG4gICAgICBGaWxlIFwiL3Vzci9sb2NhbC9saWIvcHl0aG9uMy4xMi9kaXN0LXBhY2thZ2VzL2ZseXRla2l0L2NvcmUvdXRpbHMucHlcIiwgbGluZSAzNjcsIGluIF9fY2FsbF9fXG4gICAgICAgIHJldHVybiBzZWxmLmV4ZWN1dGUoKmFyZ3MsICoqa3dhcmdzKVxuICAgICAgICAgICAgICAgXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5cbiAgICAgIEZpbGUgXCIvdXNyL2xvY2FsL2xpYi9weXRob24zLjEyL2Rpc3QtcGFja2FnZXMvZmx5dGVraXQvaW50ZXJhY3RpdmUvdnNjb2RlX2xpYi9kZWNvcmF0b3IucHlcIiwgbGluZSA0MzksIGluIGV4ZWN1dGVcbiAgICAgICAgdGFza19mdW5jdGlvbl9zb3VyY2VfZGlyID0gb3MucGF0aC5kaXJuYW1lKFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBeXl5eXl5eXl5eXl5eXl5eXG4gICAgICBGaWxlIFwiPGZyb3plbiBwb3NpeHBhdGg+XCIsIGxpbmUgMTgxLCBpbiBkaXJuYW1lXG4gICAgVHlwZUVycm9yOiBleHBlY3RlZCBzdHIsIGJ5dGVzIG9yIG9zLlBhdGhMaWtlIG9iamVjdCwgbm90IE5vbmVUeXBlXG5cbk1lc3NhZ2U6XG5cbiAgICBUeXBlRXJyb3I6IGV4cGVjdGVkIHN0ciwgYnl0ZXMgb3Igb3MuUGF0aExpa2Ugb2JqZWN0LCBub3QgTm9uZVR5cGUiLCAiY29udGVudCI6ICJ7fSIsICJzc2hVc2VkIjogIk9GRiIsICJzc2giOiAiIiwgImNvZGVzIjogW10sICJkYXRhc2V0cyI6IFtdLCAiZGF0YXN0b3JlcyI6IFtdLCAicmVzb3VyY2VEZWZpbml0aW9uIjogeyJ0aXRsZSI6ICIydkNQVSwgNEdpQiBSQU0sIDFHYnBzIiwgImNwdSI6ICIyIiwgIm1lbW9yeSI6ICI0R2kiLCAiY291bnQiOiAwfX0=")],
                volume_mounts=[],
                resources=V1ResourceRequirements(
                    limits={"cpu": "500m", "memory": "500Mi",},
                    requests={"cpu": "500m", "memory": "500Mi",},
                ),
            ),
        ],
        containers=[
            V1Container(
                name="aione-main-container",
                #image="registry-tcenter-001.dc4-faas.fzyun.io/founder/aione.ide:1.0.0.54-dev",
                image="docker.fzyun.io/founder/aione.flyteinteractive:v1.3.0",
                volume_mounts=[],
                resources=V1ResourceRequirements(
                    limits={"cpu": "2", "memory": "4Gi", "nvidia.com/gpu": "0"},
                ),
                command=command_list,
                ports=[{"containerPort": 8080, "name": "ide"}],
            )
        ],
        tolerations=[],
        image_pull_secrets= [
            #V1EnvVar(name="image-secret-ins-0e4d65d4ijfw0a6817t9268ue2")
        ],
        volumes=[]
    )
)

@task(
    container_image="aione-main-container",
    pod_template=pod_template,
)
@vscode
def task1():
    import subprocess
    import sys
    # 安装 kubernetes 包
    subprocess.run([sys.executable, "-m", "pip", "install", "kubernetes"], check=True)

    print("IDE Started.")

@workflow()
def testflow() -> str:
    task1()
    return "Ready."
