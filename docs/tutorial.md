# Python Package Development

Ah, Python packaging\! It's like assembling IKEA furniture with half the instructions and toolkit missing. If you've ever tried to create a Python package before, you're probably familiar with how complicated it gets very quickly.

(\#todo: make a cartoon)

"There should be one—and preferably only one—obvious way to do it." \- The [Zen of Python](https://en.wikipedia.org/wiki/Zen_of_Python)

"LOL" \- Python Packaging

This guide presents a consistent workflow to make Python packaging less painful and easy. We'll use a set of well tested tools while perhaps not _perfect_, work well together to automate the boring stuff and let you focus on writing code.

## Overview of this document

1. **Package structure:** Using a scaffolder (`BiocSetup & PyScaffold`) gives every project the same starting structure.
2. **Isolation for testing:** `hatchit` (or `tox` if using PyScaffold) runs tests in clean, isolated environments. This mimics how your code will run elsewhere and catches issues before your users.
3. **The `src` layout:** Putting your code in `src/package_name` prevents a common pitfall: accidentally importing your local code instead of the installed version during testing.
4. **Automation:** GitLab CI/CD or GitHub Actions handle testing, documentation builds, and publishing. Set it up once, and let the bots do all the work.
5. **Release and development cycles:** We strictly separate development (branches) from releases (tags), preventing accidental releases to PyPI or interfering with development cycles. For multi-developer projects, try to maintain master/main in a functional state and put incomplete work within a feature branch. Depending upon team size and the value of peer review, consider using pull requests prior to merging into main/master. Use [semantic versioning](https://semver.org/) for tags.

## Packaging setup

[BiocSetup](https://github.com/BiocPy/BiocSetup) (based on [hatchit](https://github.com/BiocPy/hatchit) or optionally [PyScaffold](https://pyscaffold.org/en/stable/)) automates some of the common configurtion we use across all BiocPy packages. Yes, it's a package to create packages—very meta I know :).

First, install `biocsetup` if you haven't already (`pip install biocsetup`).

Then, run the `biocsetup` command:

```sh
⋊> ~/P/scratch biocsetup my-awesome-package --description "This is going to change the world!" --license MIT
done! 🐍 🌟 ✨
BiocSetup complete! 🚀 💥
```

This command creates a complete project structure:

```sh
⋊> ~/P/my-awesome-package on master  tree -L 1
.
├── AUTHORS.md        # Who wrote this; Defaults to git user
├── CHANGELOG.md      # What changed and when?
├── CONTRIBUTING.md   # How can others help?
├── LICENSE.txt       # How can others use your code? (MIT is a good start but consult the lawyers)
├── README.md         # README of your project
├── docs              # Documentation lives here (Sphinx)
├── pyproject.toml    # Modern Python project metadata & build system config
├── setup.cfg         # The main configuration hub (metadata, dependencies, tool settings)
├── setup.py          # Mostly a shim for compatibility now, config is in setup.cfg/pyproject.toml
├── src               # <--- YOUR CODE GOES HERE!
├── tests             # <--- YOUR TESTS GO HERE!
└── tox.ini           # Configuration for testing and other tasks (tox; only if using PyScaffold)

4 directories, 9 files

```

**Markdown vs. reStructuredText:** By default, `biocsetup` uses Markdown (`.md`) as the preferred format for documentation. If you're a fan of [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) (`.rst`) or just enjoy slightly more cryptic syntax, add the `--rst` flag when running `biocsetup`. The only noticeable difference will be file extensions that make your eyes bleed (`.rst` instead of `.md`).

**Using PyScaffold for initialization:** By default, `biocsetup` relies on `hatchit` to initialize the project structure. If you prefer to use [PyScaffold](https://pyscaffold.org/) for initialization, simply add the `--pyscaffold` (or `-ps`) flag to the command.

## Adding your source code

All your Python source code goes inside the `src` directory, specifically within the subdirectory named after your package (e.g., `src/my_awesome_package/`).

```sh
src/
└── my_awesome_package/
    ├── __init__.py      # Makes it a package, exports stuff
    ├── module1.py       # Your code
    ├── another_module.py # More code
    └── _internal_utils.py # Maybe some private helpers?
```

Why `src/my_awesome_package/` and not just `my_awesome_package/` at the root? This prevents your local development code from accidentally shadowing the installed version if you happen to run Python from the project root. [Remember the xkcd cartoon?](https://xkcd.com/1987/)

### Writing and running tests

Writing code without tests is like, hmmm, thrilling, but not recommended. But then when you have too much code and no tests, it's daunting. A practice would be to write **_tests and code together_** right away\!

- **Where tests live:** All your test files go into the `tests/` directory.
- **Naming convention:** [`pytest`](https://docs.pytest.org/en/stable/) (our chosen test runner) automatically discovers test files named `test_*.py` and functions/methods named `test_*`.

```sh
tests/
├── test_core.py
└── test_edge_cases.py
```

- **Running tests:** We use [`hatchit`](https://github.com/BiocPy/hatchit) (or [`tox`](https://tox.wiki/en/4.26.0/) if you opted for PyScaffold). These tools create a temporary virtual environment, install your package and its dependencies _exactly_ as defined, and then run `pytest`. This ensures your tests run in a clean, reproducible environment, mimicking how users will install your package. Run `hatchit test` (or `tox`) to run the tests.

To run the default test suite (which includes running `pytest` and checking code coverage):

```sh
⋊> ~/P/s/my-awesome-package on master  hatchit test
.pkg: install_requires> python -I -m pip install 'setuptools>=46.1.0' 'setuptools_scm[toml]>=5'
..............
..............
..............
collected 2 items

tests/test_skeleton.py::test_fib PASSED                                               [ 50%]
tests/test_skeleton.py::test_main PASSED                                              [100%]

====================================== tests coverage =======================================
_____________________ coverage: platform darwin, python 3.12.7-final-0 ______________________

Name                                 Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------
src/my_awesome_package/__init__.py       6      0      0      0   100%
src/my_awesome_package/skeleton.py      32      1      2      0    97%   135
--------------------------------------------------------------------------------
TOTAL                                   38      1      2      0    98%
===================================== 2 passed in 0.05s =====================================
  default: OK (9.92=setup[9.26]+cmd[0.66] seconds)
  congratulations :) (10.04 seconds)
```

What's neat is that you also get coverage reports, which tell you which parts of your code are covered by tests. A reminder of all the edge cases ignored.

### "Help\! My Dependencies Are Missing\!"

Your package probably uses other Python libraries (NumPy, Pandas, etc.). If these are not listed as dependencies, your isolated test environment does not install them and you will run into errors about missing packages. Depending on your setup (hatchit vs pyscaffold), open `pyproject.toml` (and look for `dependencies`) or `setup.cfg` (and look for `install_requires`):

```yaml
[options]
install_requires =
    importlib-metadata; python_version<"3.8"
    pandas==2.0
    numpy>=1.9
    scipy~=1.3.1
    scanpy<=3.0.3; python_version>"3.10"
```

The syntax here is pretty straightforward:

- `package==2.0`: Exactly version 2.0
- `package>=1.9`: Version 1.9 or higher
- `package~=1.3.1`: Version 1.3.1 or compatible updates (1.3.\*)
- `package<=3.0.3`: Version 3.0.3 or lower

You can add Python version constraints with the semicolon notation, like `; python_version>"3.10"`. This is useful when certain packages don't play well with specific Python versions, which happens quite often.

While you're editing `setup.cfg`, also explore the package metadata, especially description, links to documentation, repository information etc.

**Note:** The fewer packages you depend on, the more sane your life will be. Especially when your dependencies are known to break things a lot and are not backwards compatible. In cases like this, **_pin_** the version of these packages\!

## Documentation with Sphinx

The scaffolding process sets up the `docs` directory with a default theme ([furo](https://github.com/pradyunsg/furo), [pydata](https://pydata-sphinx-theme.readthedocs.io/en/stable/) is another fan favorite). [Sphinx](https://www.sphinx-doc.org/en/master/) will automatically compile the docstrings in your code and generate API documentation.

- **Adding pages:**
  1. Create new Markdown (`.md`) or reStructuredText (`.rst`) files inside the `docs/` directory (e.g., `docs/tutorial.md`).
  2. Link to your new page from `docs/index.md` (or `docs/index.rst`) under the `toctree` (Table of Contents Tree) directive.
  3. By default, `docs/changelog.md` includes the content of `/CHANGELOG.md`, so you only have to update the root changelog.
  4. Write detailed docstrings and use [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) for API documentation. Docstring format is to taste, but [Google](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) or [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard) style are easily readable and both can be parsed by the [napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) Sphinx extension.
- **Building the docs:** Use `hatchit docs` (or `tox -e docs` if using PyScaffold)\! This ensures the docs build in a clean environment with all necessary extensions.

To generate the HTML files for the documentation:

```sh
⋊> ~/P/s/my-awesome-package on master  hatchit docs
docs: install_deps> python -I -m pip install -r /Users/kancherj/Projects/scratch/my-awesome-package/docs/requirements.txt
..............
..............
..............
highlighting module code... [100%] my_awesome_package.skeleton
writing additional pages... search done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded, 14 warnings.

The HTML pages are in docs/_build/html.
  docs: OK (27.45=setup[19.75]+cmd[7.70] seconds)
  congratulations :) (27.54 seconds)
```

Open `docs/_build/html/index.html` in your browser to see the results.

**Note:** The default setup includes [MyST](https://myst-nb.readthedocs.io/en/latest/) as a parser, which means you can include executable code cells in your documentation (like Jupyter Notebook cells). This is great for tutorials where users can see the code, the output, and explanations side-by-side, like in the [genomicranges tutorial](https://biocpy.github.io/GenomicRanges/tutorial.html#pandas-dataframe).

**furo vs pydata?** If you want to provide documentation for multiple releases/versions of your package, I recommend pydata. Furo currently does not support that out of the box. Checkout [sphinx-multiversion](https://github.com/sphinx-contrib/multiversion) and the corresponding [pydata page](https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html) for more details.

## Development workflows

So far, you have code, tests, and docs. How do we manage changes and release cycles?

**Fundamental Rule:** Development happens in branches, releases happen from tags. **Merging to `main`/`master` does NOT automatically release to PyPI.** This is crucial\!

**_If your documentation suggests users to clone the repo and run code, something is wrong\!\!_** Pandas or NumPy does not ask users to do this, make it easier for your users to run the tools. It not only streamlines workflows but increases accessibility, helps debug issues faster\!

#### The development cycle:

1. **Create a branch:** Need to add a feature or fix a bug? Create a descriptive branch from the latest `main` (or `master`):

```sh
git checkout main
git pull origin main
git checkout -b feature/perf
```

2. **Code & test:** Write your code in `src/`, add corresponding tests in `tests/`.
3. **Test locally:** Run `hatchit test` (or `tox`) frequently\! Catch errors early.

```sh
hatchit test
```

4. **Commit & push:** Make small, logical commits. Push your branch to GitHub. If you want to follow a structure for commits, [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) is very helpful.

```sh
git add .
git commit -m "FEAT: 10x performance"
git push origin feature/perf
```

5. **Pull Request (PR):** Go to GitHub and open a Pull Request from your branch to `main`. Describe your changes.
6. **CI checks:** GitHub Actions (configured in `.github/workflows/run-tests.yml`) will automatically run `hatchit test` (or `tox`) on your PR to ensure tests pass on different Python versions and platforms (windows, mac and linux).
7. **Merge:** Once reviewed and CI passes, merge the PR into `main`.
8. **Repeat:** Continue the cycle for the next feature or fix.

#### The Release Cycle (Deploying to PyPI):

When you decide that the current state of `main` is ready for users:

1. **Ensure `main/master` is clean:** Make sure the `main` branch is up-to-date and all tests pass.
2. **Update `CHANGELOG.md`:** Document the new version's changes. [Keepachangelog](https://keepachangelog.com/en/1.0.0/) has a good guide on what and how to document. If you follow conventional commits, there are tools that can automate your changelog generation.
3. **Tag the release:** Create a Git tag matching the version number (e.g., `0.1.0`).

```sh
git checkout main
git pull origin main
git tag 0.1.0 -m "Release version 0.1.0"
git push origin 0.1.0 # <--- Push the tag!
```

4. **Automation takes over:** Pushing the tag triggers a specific GitHub Action (`.github/workflows/publish-pypi.yml`):
   - It checks out the tagged commit.
   - It runs tests one last time (just in case).
   - It builds the package (source distribution and wheel).
   - It builds the documentation.
   - It **publishes the package to PyPI** using "Trusted Publishing" ([instructions](https://docs.pypi.org/trusted-publishers/), no API tokens needed in GitHub).
   - It deploys the documentation to GitHub Pages.
5. **Celebrate\!** Your package is live\! Announce it to your users.

#### Notes on versioning

One aspect of packaging that often gets overlooked is proper versioning. Here's a quick primer on semantic versioning (semver):

1. **MAJOR version**: Increment when you make incompatible API changes
2. **MINOR version**: Increment when you add functionality in a backward-compatible manner
3. **PATCH version**: Increment when you make backward-compatible bug fixes

In practice, this looks like `1.2.3` (major.minor.patch).

The scaffolding uses `setuptools_scm` to manage your version numbers automatically based on git tags. This is incredibly handy because:

1. You don't have to manually update version numbers in your code
2. The version will always reflect the state of your git repository
3. Development versions will have suffixes like `.dev1+g1234abc`

To release a new version, just create a git tag:

```sh
git tag -a 0.1.0 -m "Initial release"
git push --tags
```

This not only marks the release in your git history but also sets the version for your package when it's built.

## Coding standards & linting

Consistent code is easier to read, review, and maintain.

- **Style guides:** Follow the [BiocPy Developer Guide](https://github.com/BiocPy/developer_guide) and/or the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- **Automated checks (`pre-commit-bot`):** The scaffold sets up `pre-commit`. This runs tools automatically, catching formatting issues, linting errors, and other common problems.
  - Enable the [pre-commit bot](https://pre-commit.ci/) for your repository
  - **Tools:** It typically runs:
    - **[`ruff`](https://docs.astral.sh/ruff/):** An extremely fast linter and formatter that catches _tons_ of potential issues and style violations.
    - Maybe [`black`](https://github.com/psf/black) for opinionated formatting (often handled by `ruff` now).
    - Checks for large files, leftover merge conflict markers, etc.
- **Code coverage (`codecov`):** Enable the [Codecov](https://about.codecov.io/) GitHub app on your repository. The workflows are usually pre-configured to upload coverage reports. This gives you nice visualizations of test coverage over time and on PRs.

## Extras

- **Interfacing with C++:** Integrating C++ code is possible but more involved (usually using `pybind11`). The core packaging process is similar, but you'll have slightly different build steps and different GitHub Actions configurations. Check out [IRanges](https://github.com/BiocPy/IRanges), [scranpy](https://github.com/libscran/scranpy), [rds2py](https://github.com/BiocPy/rds2py) etc for examples, and reach out for help.
  - [scikit-build](https://scikit-build.readthedocs.io/en/latest/) also provides a process to interface with c++ code
- **Publish to conda-forge/bioconda:** Publishing to these registries is pretty straightforward for pure python packages, it's a bit more involved for packages with C++ bindings, e.g. check out our [PR](https://github.com/conda-forge/staged-recipes/pull/29764) to get a couple of BiocPy packages into conda-forge.
- **Control files in the distribution:** Use [MANIFEST.IN](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html) to set up rules to ignore folders or files in the source that do not need to be in the generated wheels and installation files.
- **Are you a Rust enthusiast?** Check out [PyO3](https://pyo3.rs/v0.25.0/).

## Other tools/guides to explore:

- Info on [setuptools](https://setuptools.pypa.io/en/latest/index.html), that our scaffolding tool uses
- [PyOpenSci's python package guide](https://www.pyopensci.org/python-package-guide/index.html)
- Get familiar with [git](https://git-scm.com/), or if you want to get fancy, use [jujustu](https://github.com/jj-vcs/jj)
- There are many alternatives to each of the tools mentioned here
  - [quartodoc](https://github.com/machow/quartodoc)/[mkdocs](https://www.mkdocs.org/) instead of Sphinx
  - [nox](https://nox.thea.codes/en/stable/) or [tox](https://tox.wiki/en/4.26.0/) instead of hatchit
  - [poetry](https://python-poetry.org/) and [hatch](https://hatch.pypa.io/) (probably go with the later since its developed by the official PyPI working group on packaging) instead of setuptools

## Conclusion

And that's the gist of it\! It might seem like a lot initially, but once you go through the cycle a couple of times, it becomes second nature. Remember the key steps: scaffold, code in `src/`, test in `tests/` (run with `hatchit test`), manage dependencies, document in `docs/` (build with `hatchit docs`), use branches for development, and tag for releases.
