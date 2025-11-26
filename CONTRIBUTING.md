
# 🤖 nRobo – NextGen Test Automation Framework

**nrobo** is a modular, YAML-driven test automation framework powered by PyTest, designed for web automation teams that value simplicity, flexibility, and CI/CD readiness.

# Contributing to nRobo 🛠️

Thank you for your interest in contributing to **nrobo**. We welcome all kinds of contributions — bug reports, new features, documentation improvements — and we appreciate your help in making this project better for everyone.

## ✅ What kinds of contributions we welcome

- Bug reports / bug fixes
- New features, enhancements, or integrations (e.g. new reporters, loaders, utilities)
- Documentation improvements (README, docs, examples, tutorials)
- Test cases, especially for new functionality or edge cases
- CI/CD, packaging improvements, dev‑tooling, automation

## 📦 Getting started (development setup)

To set up your local development environment:

```bash
  # clone repo
  git clone https://github.com/pancht/nrobo.git
  cd nrobo

  # install virtual envrionment
  python -m venv .venv      # or your preferred venv tool
  source .venv/bin/activate  # (on Windows use `.venv\\Scripts\\activate`)

  #install pre-requisites
  pip install -r requirements.txt

  # Activate pre-commit for git hooks. Ensure code quality.
  pre-commit install

  # Install this project in editable mode from the current directory (.).
  pip install -e .

  # initialize nRobo
  nrobo --init
```

You can then run the existing test suite with:

```bash
  # Get nRobo command line help
  nrobo --help # Get command line help

  # Execute tests
  nrobo

  # Execute a suite
  nrobo --suite google_test_suite.yml

  # Execute multiple suites
  nrobo --suite google_test_suite.yml sample_suite_another.yml

  # Execute tests in parallel
  nrobo -n 2 # two tests run in concurrency

  # Execute tests in parallel on firefox browser
  nrobo -n 2 --browser firefox

  # Execute tests in parallel on firefox browser in non-headless (UI) mode
  # This is because nRobo by default runs UI tests in headless mode.
  # That is why you need to supply --no-headless switch to run in UI mode.
  nrobo -n 2 --browser firefox --no-headless
```

We enforce formatting and linting standards — before submitting changes, please run:

```bash
  black src/ tests/
  flake8 src/ tests/
  pytest --cov=src/
```

If you add new functionality, please add appropriate test coverage.

# 🔧 How to contribute code

We use the standard fork → branch → pull request (PR) workflow:

1. Fork the repository

1. Create a new branch for your work (git checkout -b feature/my-feature or bugfix/issue-123)

1. Make your changes, and ensure tests pass + code is formatted and linted

1. Update documentation as needed (README, docs, docstrings)

1. Commit with a clear, descriptive message

1. Push your branch and open a Pull Request, describing what you changed and why

If your change is substantial, it may help to first open an Issue to discuss the idea.

Once the PR is submitted, maintainers will review. Aim for clarity, simplicity, and maintainability.

# 🐛 Reporting bugs or requesting features

If you spot a problem or want to propose a new feature:

- First search existing Issues to see if it’s already reported/requested

- If not, open a new Issue following the issue template (when available), and provide:

    - clear description of the bug or request

    - steps to reproduce (for bugs) or a rationale (for enhancements)

    - expected vs. actual behavior (for bugs)

    - environment info (OS, Python version, browser, etc. if relevant)

Good bug reports save time for everyone!

# 📚 Coding style & standards

- Follow existing code style (formatting, naming, docstrings)

- Use black for formatting and flake8 for linting (as used currently)

- Write unit tests for new functionality or reproducible bug fixes

- Keep code modular, maintainable, and well-documented

# 🙋 Other ways to contribute (non‑code)

- Improve documentation: README, docs, tutorials, examples

- Suggest new use‑cases or features via Issues or Discussions

- Review and comment on others’ pull requests

- Help triage issues: reproduce bug reports, verify feature requests, close duplicates

# 📄 License & Code of Conduct

By contributing, you agree that your contributions will be licensed under the project’s existing license (MIT). Please ensure any added code/documents are compatible with MIT licensing.

Also, please ensure that all interactions (issues, PRs, comments) are respectful and constructive. Kindness and collaboration make open‑source possible.

# 🙌 Thank you

We appreciate your time, effort, and contributions. Your help makes nrobo stronger and more useful for everyone.
