from nrobo.exceptions import DependencyNotFoundError


def check_dependency(name: str, install_hint: str | None = None):
    import shutil

    if shutil.which(name) is None:
        raise DependencyNotFoundError(name, install_hint)
