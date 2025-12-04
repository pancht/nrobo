
# 🤖 nrobo – NextGen Test Automation Framework

**nrobo** is a modular, YAML-driven test automation framework powered by PyTest, designed for web automation teams that value simplicity, flexibility, and CI/CD readiness.


---

[![CI](https://github.com/pancht/nrobo/actions/workflows/ci.yml/badge.svg)](https://github.com/pancht/nrobo/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pancht/nrobo/branch/production/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/pancht/nrobo)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/pancht/nrobo/blob/production/LICENSE)
[![Watch on YouTube](https://img.shields.io/badge/YouTube-Playlist-red?logo=youtube&logoColor=white)](https://youtube.com/playlist?list=PLMkFSH7JcxPGXo5D3tesuUQcDqUPeE-ZL&si=uD3TCu6KpKDKV3G7)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/nrobo?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/nrobo)

# Architecture

> ℹ️ See [docs/architecture.md](docs/architecture.md) for the nRoBo architecture diagram and design details.

## 🚀 Features

- ✅ **PyTest-Powered Engine** – built on the rock-solid `pytest` foundation
- 🧱 **Modular Architecture** – decoupled loader, executor, and reporter components
- 📜 **YAML-Based Test Suites** – write tests in a human-readable format
- 🖥️ **Selenium Web Integration** – cross-browser support (Chrome, Firefox, Edge)
- 📊 **Allure + HTML Reporting** – customizable test reports with logs and screenshots
- 🔧 **Reusable Steps & Configs** – DRY principle applied across suites
- 🔁 **Data-Driven Testing** – externalize inputs for flexible test coverage
- 🧪 **Self-Tested Framework** – internal tests for reliability
- 📦 **Modern Packaging** – install via `pip`, structured with `pyproject.toml`
- 🛡️ **Security Audited** – integrates with `bandit` and `pip-audit`
- ⚙️ **CI/CD Friendly** – GitHub Actions-ready out of the box

---


## 🧰 Pre-requisites

- Install Python (3.11 or higher)
  - python --version
- Install Java (11  or higher)
- Install allure command line tool.
  - Check [Install guide](https://allurereport.org/docs/gettingstarted-installation/)
        - Run the following command to check if allure cli is installed

```bash
  allure --version
````


## 📦 Installation

- Make a directory for automation project
```bash
  mkdir dream
  cd dream
```
- Install **virtualenv** package

```bash
  pip install virtualenv
```
- Create virtual environment - `.venv`

```bash
  virtualenv .venv
```
- Activate virtual environment
  - Unix/Mac/Linux
    - `source .venv/bin/activate`
  - Windows
    - `.\\.venv\\Scripts\\activate`

- Install *nrobo*

```bash
  pip install nrobo
  nrobo --init
  nrobo # This will run sample tests
```

- Other ways to work with `nrobo`
```bash
    nrobo -s
    nrobo -n 2 -s
    nrobo --co
```
**Or** Setup local development environment:

- [On MacOS](https://github.com/pancht/nrobo/wiki/Local-Development-Setup-(macOS))



🧪 Quick Start

```bash
nrobo --suite suites/login_test.yaml
```

**Or** run via `pytest` if testing a local implementation:

```bash
nrobo -suite=suites/login_test.yaml
```

🧱 Directory Structure

```bash
nrobo/
├── src/nrobo/         ← Core framework (loader, executor, reporter)
├── suites/            ← YAML-defined test suites
├── tests/             ← Unit/integration tests for framework
├── docs/              ← Architecture docs, diagrams, examples
├── pyproject.toml     ← Packaging configuration
└── build_and_publish.py
```

📊 Reports

After execution, you'll get rich test reports:

- **Allure Report:**

```bash
allure serve results/
```

- **HTML Report:**

Open **reports/report.html** in your browser.

🛠️ Developer Guide

Run code checks:

```bash
black src/ tests/
flake8 src/ tests/
pytest --cov=src/
```

📚 Documentation

- Getting Started
- Writing Test Suites
- Architecture Diagram
- Extending nrobo

👥 Contributing

Want to add your own modules or reporters? Open a pull request or start a discussion!

- Fork this repo

- Create a feature branch

- Add tests for new logic

- Run `black`, `flake8`, and `pytest`

- Submit your PR with a detailed description

📝 License
MIT © 2025 pancht

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/pancht/nrobo/blob/production/LICENSE)
