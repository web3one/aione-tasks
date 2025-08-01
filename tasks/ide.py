from flytekit import task, workflow
from flytekitplugins.flyteinteractive import vscode


@task
@vscode
def train():
    print("forward")
    print("backward")


@workflow
def wf_train():
    train()


if __name__ == "__main__":
    wf_train()
