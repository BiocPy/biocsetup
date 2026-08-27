import os
import tempfile
from pathlib import Path

import pytest

from biocsetup.create_repository import create_repository

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_create_repository_pyscaffold(temp_dir):
    """Test basic repository creation with pyscaffold."""
    project_name = "test_project"
    project_path = os.path.join(temp_dir, project_name)

    create_repository(
        project_path=project_path,
        description="Test project",
        use_pyscaffold=True
    )

    assert os.path.exists(project_path)
    assert os.path.exists(os.path.join(project_path, "src"))
    assert os.path.exists(os.path.join(project_path, "docs"))
    assert os.path.exists(os.path.join(project_path, ".github", "workflows", "run-tests.yml"))

    conf_py = Path(project_path) / "docs" / "conf.py"
    assert conf_py.exists()

def test_create_repository_with_description_pyscaffold(temp_dir):
    project_path = os.path.join(temp_dir, "test-desc-project")
    description = "Custom project description"

    create_repository(
        project_path=project_path,
        description=description,
        use_pyscaffold=True
    )

    readme_path = Path(project_path) / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()
        assert description in content

def test_create_repository_with_license_pyscaffold(temp_dir):
    project_path = os.path.join(temp_dir, "test-license-project")
    license = "BSD"

    create_repository(
        project_path=project_path,
        license=license,
        use_pyscaffold=True
    )

    setup_cfg = Path(project_path) / "setup.cfg"
    with open(setup_cfg, "r") as f:
        content = f.read()
        assert license in content

def test_create_repository_with_rst_pyscaffold(temp_dir):
    project_path = os.path.join(temp_dir, "test_t_rst")

    create_repository(
        project_path=project_path,
        rst=True,
        use_pyscaffold=True
    )

    index_rst = Path(project_path) / "docs" / "index.rst"
    assert os.path.exists(str(index_rst))

def test_create_repository_hatchit_default(temp_dir):
    project_path = os.path.join(temp_dir, "test-hatchit")

    create_repository(
        project_path=project_path,
        description="Hatchit default test",
        license="MIT"
    )

    # Check hatchit specific files
    assert os.path.exists(os.path.join(project_path, "pyproject.toml"))
    assert os.path.exists(os.path.join(project_path, "tox.ini"))
