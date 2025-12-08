
# 🤖 nRobo — Next-Gen Test Automation for Selenium (with Playwright Superpowers)

**nrobo** is a modular, YAML-driven test automation framework powered by PyTest, designed for web automation teams that value simplicity, flexibility, and CI/CD readiness.


---

<p align="center">
<a href="https://github.com/pancht/nrobo/actions/workflows/ci.yml"><img src="https://github.com/pancht/nrobo/actions/workflows/ci.yml/badge.svg"></a>
<a href="https://codecov.io/gh/pancht/nrobo"><img src="https://codecov.io/gh/pancht/nrobo/branch/production/graph/badge.svg?token=YOUR_TOKEN"></a>
<a href="https://github.com/pancht/nrobo/blob/production/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
<a href="https://youtube.com/playlist?list=PLMkFSH7JcxPGXo5D3tesuUQcDqUPeE-ZL&si=uD3TCu6KpKDKV3G7"><img src="https://img.shields.io/badge/YouTube-Playlist-red?logo=youtube&logoColor=white"></a>
<a href="https://pypi.org/project/nrobo/"><img src="https://static.pepy.tech/personalized-badge/nrobo?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads"></a>
<a href="https://pypi.org/project/nrobo/"><img src="https://img.shields.io/pypi/v/nrobo.svg?color=brightgreen"></a>
<a href="https://pypi.org/project/selenium/"><img src="https://img.shields.io/badge/Selenium-4%2B-orange"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue"></a>
</p>



> nRobo modernizes Selenium with Playwright-style selectors, auto-wait engine, locator collections, and full compatibility with existing Selenium code.
It brings stability, expressiveness, and speed to UI test automation — all powered by PyTest.

## 📘 Table of Contents
- Architecture
- Why nRobo?
- Features
- Install & Setup
- Quick Start
- Writing Tests
- Selector Engine
- Locator Collections
- AutoWait Engine
- Reports
- Contributing
- License

### Architecture

> ℹ️ See [docs/architecture.md](docs/architecture.md) for the nRoBo architecture diagram and design details.
> nRobo is built on a modular architecture with clear separation between loader, executor, selector engine, autowait engine, and reporters.
>
### ⭐️ Why nRobo?
- 🧠 Because Selenium needs modern selectors.
- ⚙️ Because Playwright's power should work everywhere.
- 🔥 Because flaky tests waste time — stability should be automatic.

**nRobo** solves all three.

## 🚀 Features

1. ✅ **PyTest-Powered Engine** – built on the rock-solid `pytest` foundation
2. 📊 **Allure + HTML Reporting** – customizable test reports with logs and screenshots
3. 🌀 **Integrated Nginx Allure Server** – serves Allure reports without needing the Allure CLI, and includes simple start, status, and stop commands for hassle-free report hosting
4. 🖥️ **Selenium Web Integration** – cross-browser support (Chrome, Firefox, Edge)
5. 🧱 **Modular Architecture** – decoupled loader, executor, and reporter components
6. 📸 **Screenshots on Failure** - Automatically captures and attaches browser screenshots when a test fails — works with both HTML reports and Allure reports for instant visual debugging.
7. 🕒 **Logs & Timestamps** - Every test run includes detailed logs with timestamps, durations, and structured formatting — making it easy to trace failures, slow steps, and unexpected behavior.
8. 📜 **YAML-Based Test Suites** – write tests in a human-readable format
9. 🧪 **Self-Tested Framework** – internal tests for reliability
10. 📦 **Modern Packaging** – install via `pip`, structured with `pyproject.toml`
11. 🛡️ **Security Audited** – integrates with `bandit` and `pip-audit`
12. ⚙️ **CI/CD Friendly** – GitHub Actions-ready out of the box
13. 🧠 Powercharged Selenium with the following:
    1. **Advanced Selector Engine (Playwright-Level)** - Supports everything you know from Playwright — but works on Selenium:
       - text=Login, "Login", regex /login/i
       - button:visible, input:enabled, :checked, :not(.disabled)
       - :has() nested selectors
       - :has-text()
       - shadow:: pierce selectors (>>>)
    ```css
    form:has(input[name=email]) >> button:visible
    shadow::todo-app >>> li:has-text("Done")
    ```
    2. 🧩 **Smart Locator & Collection API** - Like Playwright, but runs on Selenium:
    ```python
    page.locator("#email").fill("admin@example.com").press("Enter")
    page.locator("div.card:has(.price)").nth(2).click()
    page.locator("li.item").all().filter(has_text="Active").first().click()
    ```
    3. **Collection features:**
       - .all()
       - .first(), .last(), .nth(i)
       - .filter(), .map(), .slice()
       - Set operations: union, intersection, difference
       - .random()

    1. ⚙️ **AutoWait & Stability Engine** - Eliminates 95% of test flakiness:

       - Built-in retries

       - Scroll into view before action

       - Automatic visibility checks

       - Stale element recovery

       - WebDriverWait built into every action

       - No sleeps, no explicit waits needed

        Example:

        ```python
        page.locator("#login").click()   # waits automatically
        page.locator("#email").fill("user")
        ```

    1. 🌐 **Deep Selenium Compatibility Layer**
       - Works with all WebDrivers (Chrome, Edge, Firefox, Safari)

       - Full WebElement support through __getattr__

       - ActionChains support (hover, drag, double_click)

       - Selenium-based typing (Protocol) ensures autocomplete

        You can always fall back to raw Selenium if needed:

        ```python
        page.locator("#submit")._find().get_attribute("class")
        ```

    1. 📚 **Developer Experience & Extensibility**
       - Clean, modern API design

       - Fully typed (Protocol-based)

       - Modular selector engine (easy to extend)

       - Add your own pseudo selectors

       - Build your own condition helpers

       - Elegant plugin architecture (coming soon)

    1. 🔍 **Example: Complex Selecto**

        Playwright-style selectors on Selenium:

        ```python
        page.locator(
            "form:has(input[name=email]) >> button:has-text('Submit'):visible"
        ).click()
        ```

    1. **Shadow DOM support:**

        ```python
        page.locator("shadow::todo-app >>> li:has-text('Completed')").click()
        ```

    1. **Nested filters:**

        ```python
        rows = page.locator("tr:visible").all()
        rows.filter(has_text="Active").nth(0).click()
        ```

## 🚀 Upcoming Features
- 🔧 **Reusable Steps & Configs** – DRY principle applied across suites
- 🔁 **Data-Driven Testing** – externalize inputs for flexible test coverage

---

## 🔥 Feature Comparison
| Feature                | Selenium    | Playwright  | nRobo |
| ---------------------- |-------------|-------------|-------|
| CSS Selectors          | ✅          | ✅          | ✅    |
| Text Selectors         | ❌          | ✅          | ✅    |
| has-text()             | ❌          | ✅          | ✅    |
| has()                  | ❌          | ✅          | ✅️    |
| :visible, :enabled     | ❌          | ✅          | ✅    |
| Shadow DOM             | ⚠️ limited  | ✅          | ✅    |
| AutoWait               | ❌          | ✅          | ✅    |
| Locator Collections    | ❌          | ✅          | ✅    |
| Selenium Compatibility | ✅          | ❌          | ✅    |
nRobo = **Playwright power** + **Selenium compatibility**.

## 🧰 Pre-requisites

- Install Python (3.11 or higher)
  - python --version

## 📦 Installation

### Make a directory for automation project
```bash
  mkdir <test_project_name>
  cd <test_project_name>
```
### Install ***venv*** package
  - 🔵 macOS: No installation needed — macOS Python includes venv.
  - 🟢 Ubuntu / Debian Linux:
    - `sudo apt update`
    - `sudo apt install python3-venv`
  - 🔶 RedHat / CentOS / Fedora:
    - `sudo dnf install python3-venv`
  - 🟣 Windows: No installation needed — Also included by default.

###   Create virtual environment - `.venv`

```bash
  python -m venv .venv
```
### Activate virtual environment
  - Unix/Mac/Linux
    - `source .venv/bin/activate`
  - Windows
    - `.\\.venv\\Scripts\\activate`

### Install *nrobo*

```bash
  # Install nrobo
  pip install nrobo

  # initialize project
  nrobo init --app <project_name>

  # run sample tests
  nrobo # This will run sample tests
```

#### Other ways to work with `nrobo`
```bash
    # run tests disabled output capturing
    # means prints will not be captured and shows up on console right away
    nrobo -s

    # run 2 tests in parallel with disabled output capturing
    nrobo -n 2 -s

    # collect tests and show them on console. do not execute them!
    nrobo --co
```

#### Example test:
```python
def test_login(page):
    page.locator("text=Login").click()
    page.locator("#email").fill("admin")
    page.locator("#password").fill("secret")
    page.locator("button:has-text('Login')").click()
    page.locator("text=Welcome").should_be_visible()
```

#### 🧰 Built-in Helpers
##### Conditions
```python
page.locator("#item").should_be_visible()
page.locator("button").should_be_enabled()
page.locator("input").should_have_text("Hello")
```

##### Collections
```python
items = page.locator("li").all()
assert items.count() == 5
```

##### Advanced Operations
```python
active = items.filter(has_text="Active")
remaining = items.difference(active)
```

**Or** Setup local development environment:

- [On MacOS](https://github.com/pancht/nrobo/wiki/Local-Development-Setup-(macOS))



## 🧪 Quick Start

```bash
# run login_test test suite only
nrobo --suite suites/login_test.yaml
```

## **Or** run via `pytest` if testing a local implementation:

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

# 📊 Reports

After execution, nrobo will generate html and allure report through integrated **pytest-html** and **pytest-allure** plugins.
nRobo will share following in console:
1. Link of html report
2. Link of allure report
3. Sets up local nginx server, and serve allure report for visualization with localhost url.

![img.png](images/img.png)

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
