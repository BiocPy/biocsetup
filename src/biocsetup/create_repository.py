import shutil
import subprocess
from pathlib import Path
import datetime

from pyscaffold import api, file_system, shell
from pyscaffoldext.markdown.extension import Markdown

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def create_repository(
    project_path: str,
    description: str | None = "Add a short description here!",
    license: str = "MIT",
    rst: bool = False,
    use_pyscaffold: bool = False,
) -> None:
    """
    Create a new BiocPy Python package repository.

    Args:
        project_path:
            Path where the new project should be created.

        description:
            Optional project description.

        license:
            License to use.
            Defaults to 'MIT'.

        rst:
            Whether to use 'markdown' or 'rst'.
            Defaults to False, to use 'markdown'.
    """
    if not use_pyscaffold:
        try:
            from hatchit.scaffold import create_hatchit_repository
            return create_hatchit_repository(project_path, description, license)
        except ImportError:
            import sys
            print("Error: The 'hatchit' package is required for default scaffolds.")
            print("Please install it in your environment: pip install hatchit")
            sys.exit(1)

    # Create project using pyscaffold with markdown extension
    if description is None:
        description = "Add a short description here!"

    extensions = []
    if not rst:
        extensions = [Markdown()]

    opts = {
        "project_path": project_path,
        "description": description,
        "license": license,
        "extensions": extensions,
    }
    api.create_project(**opts)

    modified_files = []

    # Get absolute path to templates directory
    template_dir = Path(__file__).parent / "templates"

    # Add GitHub Actions
    gh_actions_dir = Path(project_path) / ".github" / "workflows"
    gh_actions_dir.mkdir(parents=True, exist_ok=True)

    for workflow in ["run-tests.yml", "publish-pypi.yml"]:
        src = template_dir / "github_workflows" / workflow
        dst = gh_actions_dir / workflow
        shutil.copy2(src, dst)
        modified_files.append(dst)

    # Add pre-commit config
    precommit_src = template_dir / "precommit" / "pre-commit-config.yaml"
    precommit_dst = Path(project_path) / ".pre-commit-config.yaml"
    shutil.copy2(precommit_src, precommit_dst)
    modified_files.append(precommit_dst)

    # Modify sphinx conf.py
    conf_py_path = Path(project_path) / "docs" / "conf.py"
    with open(conf_py_path, "r") as f:
        conf_content = f.read()

    # Add myst-nb extension and configuration
    myst_config = """

# -- Biocsetup configuration -------------------------------------------------

# Enable execution of code chunks in markdown
extensions.remove('myst_parser')
extensions.append('myst_nb')

# Less verbose api documentation
extensions.append('sphinx_autodoc_typehints')

autodoc_default_options = {
    "special-members": True,
    "undoc-members": True,
    "exclude-members": "__weakref__, __dict__, __str__, __module__",
}

autosummary_generate = True
autosummary_imported_members = True

html_theme = "furo"
"""

    # conf_content = conf_content.replace("alabaster", "furo")

    with open(conf_py_path, "w") as f:
        f.write(conf_content + myst_config)
        modified_files.append(conf_py_path)

    # Update requirements.txt for docs
    docs_requirements = Path(project_path) / "docs" / "requirements.txt"
    with open(docs_requirements, "a") as f:
        f.write("myst-nb\nfuro\nsphinx-autodoc-typehints\nlinkify-it-py\n")
        modified_files.append(docs_requirements)

    # Modify README
    readme_path = Path(project_path) / "README.md"
    proj_name = Path(project_path).parts[-1]

    new_readme = f"""[![PyPI-Server](https://img.shields.io/pypi/v/{proj_name}.svg)](https://pypi.org/project/{proj_name}/)
![Unit tests](https://github.com/YOUR_ORG_OR_USERNAME/{proj_name}/actions/workflows/run-tests.yml/badge.svg)

# {proj_name}

> {description}

A longer description of your project goes here...

## Install

To get started, install the package from [PyPI](https://pypi.org/project/{proj_name}/)

```bash
pip install {proj_name}
```

<!-- biocsetup-notes -->

## Note

This project has been set up using [BiocSetup](https://github.com/biocpy/biocsetup)
and [PyScaffold](https://pyscaffold.org/).
"""

    with open(readme_path, "w") as f:
        f.write(new_readme)
        modified_files.append(readme_path)

    # Modify ppyproject.toml to add ruff configuration
    pyprj_path = Path(project_path) / "pyproject.toml"
    with open(pyprj_path, "r") as f:
        pyprj_content = f.read()

    ruff_config = """
[tool.ruff]
line-length = 120
src = ["src"]
exclude = ["tests", "docs"]

[tool.ruff.lint]
extend-ignore = ["F821"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]

[tool.ruff.format]
docstring-code-format = true
docstring-code-line-length = 20
"""

    with open(pyprj_path, "w") as f:
        f.write(pyprj_content + ruff_config)
        modified_files.append(pyprj_path)

    with file_system.chdir(project_path):
        for f in modified_files:
            shell.git("add", str(f.relative_to(project_path)))

        try:
            # Check if git user config exists before committing
            import subprocess
            name_configured = subprocess.run(["git", "config", "user.name"], capture_output=True).returncode == 0
            email_configured = subprocess.run(["git", "config", "user.email"], capture_output=True).returncode == 0
            
            if name_configured and email_configured:
                shell.git("commit", "-m", "BiocSetup configuration")
        except Exception:
            pass  # Git commit is optional

    print("BiocSetup complete! 🚀 💥")


