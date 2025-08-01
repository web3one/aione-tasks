from flytekit import task, workflow,Resources
from flytekitplugins.flyteinteractive import vscode


@task(
    container_image="ghcr.io/flyteorg/flytekit:flyteinteractive-latest",
    requests=Resources(cpu="1", mem="2000Mi"),
)

@vscode
def train():
    print("forward")
    print("backward")


@workflow
def wf_train():
    train()


if __name__ == "__main__":
    wf_train()
