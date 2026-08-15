from click.testing import CliRunner
import os
import tempfile
from pathlib import Path

import pytest

from biocsetup.cli import main

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def test_cli_basic():
    """Test basic CLI functionality with minimal arguments."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["test-project"])
        assert result.exit_code == 0

        # Check if project was created
        assert os.path.exists("test-project")
        assert os.path.exists(os.path.join("test-project", "src"))
        assert os.path.exists(os.path.join("test-project", "docs"))

def test_cli_with_options():
    """Test CLI with all optional arguments."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "test-project",
                "--description", "Test project description",
                "--license", "BSD",
            ]
        )
        assert result.exit_code == 0

        # Check if project was created
        project_dir = Path("test-project")
        assert project_dir.exists()

        # Check if description was added to README
        readme_content = (project_dir / "README.md").read_text()
        assert "Test project description" in readme_content

        # Check if license was set correctly
        setup_cfg = (project_dir / "setup.cfg").read_text()
        assert "BSD" in setup_cfg

def test_cli_invalid_path():
    """Test CLI with invalid project path."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a file that will conflict with the project path
        with open("existing-file", "w") as f:
            f.write("test")

        result = runner.invoke(main, ["existing-file"])
        assert result.exit_code != 0

def test_cli_help():
    """Test CLI help output."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Create a new BiocPy Python package" in result.output
    assert "--description" in result.output
    assert "--license" in result.output
    assert "--uv" in result.output

def test_cli_with_uv():
    """Test CLI with --uv option."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "test-project-uv",
                "--uv",
                "--description", "Test project description with uv",
                "--license", "MIT",
            ]
        )
        assert result.exit_code == 0

        # Check if project was created
        project_dir = Path("test-project-uv")
        assert project_dir.exists()

        # Check if pyproject.toml exists and has the description
        pyproject_content = (project_dir / "pyproject.toml").read_text()
        assert "Test project description with uv" in pyproject_content

        # Check if tests directory was created
        assert (project_dir / "tests" / "test_basic.py").exists()
        
        # Check if github workflows were copied
        assert (project_dir / ".github" / "workflows" / "run-tests.yml").exists()
