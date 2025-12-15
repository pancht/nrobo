
# 🤖 nRobo — Next-Gen Test Automation for Selenium (with Playwright Superpowers)

**nRobo** brings the modern selector engine, autowait magic, and fluent APIs of **Playwright**, while staying fully compatible with **Selenium WebDriver**.

It’s built for QA teams who want **stability, readability, and zero flakiness** — without migrating away from the Selenium ecosystem.

---

<p align="center">
<a href="https://github.com/pancht/nrobo/actions/workflows/ci.yml"><img src="https://github.com/pancht/nrobo/actions/workflows/ci.yml/badge.svg"></a>
<a href="https://codecov.io/gh/pancht/nrobo"><img src="https://codecov.io/gh/pancht/nrobo/branch/production/graph/badge.svg?token=YOUR_TOKEN"></a>
<a href="https://github.com/pancht/nrobo/blob/production/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
<a href="https://youtube.com/playlist?list=PLMkFSH7JcxPGXo5D3tesuUQcDqUPeE-ZL&si=uD3TCu6KpKDKV3G7"><img src="https://img.shields.io/badge/YouTube-Playlist-red?logo=youtube&logoColor=white"></a>
<a href="https://pepy.tech/projects/nrobo"><img src="https://static.pepy.tech/personalized-badge/nrobo?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads"></a>
<a href="https://pypi.org/project/nrobo/"><img src="https://img.shields.io/pypi/v/nrobo.svg?color=brightgreen"></a>
<a href="https://pypi.org/project/selenium/"><img src="https://img.shields.io/badge/Selenium-4%2B-orange"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue"></a>
</p>



> Modern selectors + AutoWait + Collections + Allure reporting + CI-ready packaging.
**nRobo = Playwright-level power with Selenium-level compatibility**.


## ⭐️ Why nRobo?
### Because Selenium is powerful — but outdated.
### Because Playwright is modern — but incompatible with Selenium ecosystems.
### Because flaky UI tests cost time, money, and reputation.

**nRobo solves all three***.

## 🚀 30-Second Quick Demo

```python
def test_login(page):
    page.selector("text=Login").click()
    page.selector("#email").fill("admin")
    page.selector("#password").fill("secret")
    page.selector("button:has-text('Login')").click()
    page.selector("text=Welcome").should_be_visible()
```

This works on **Selenium**, but feels like **Playwright**.

## 🔥 nRobo vs Selenium vs Playwright

| Capability                        | Selenium | Playwright | nRobo         |
| --------------------------------- | -------- | ---------- | ------------- |
| AutoWait on all actions           | ❌        | ✅          | ✅             |
| text= selectors                   | ❌        | ✅          | ✅             |
| has-text(), has()                 | ❌        | ✅          | ✅             |
| Shadow DOM >>>                    | ⚠️       | ✅          | ✅             |
| Locator Collections               | ❌        | ✅          | ✅             |
| Chaining: click().fill().should() | ❌        | ❌          | ✅ (Exclusive) |
| Selenium WebDriver support        | ✅        | ❌          | ✅             |

> nRobo = **Playwright’s power** + **Selenium’s reach** + **its own exclusive features**

## ✨ Exclusive Features (Only in nRobo)
### 1. [Locator Action Chaining (Exclusive)](https://github.com/pancht/nrobo/blob/production/docs/locator_action_chaining.md)

A fluent API inspired by Playwright but designed for Selenium:
```python
page.selector("input").click().locator("#email").fill("admin").should_be_visible()
```

Mix CSS, XPath, Text, Regex, Pseudo, and Shadow selectors seamlessly.

### 🔧 Enable/Disable:
```python
settings.ENABLE_LOCATOR_ACTION_CHAINING = True
```

### 📄 Full documentation:
➡️ [docs/locator_action_chaining.md](https://github.com/pancht/nrobo/blob/production/docs/locator_action_chaining.md)

## 2. Advanced Selector Engine (Playwright-level)

Supported:

- `text=Login`

- `"Login"`

- `regex: /login/i`

- `:visible, :enabled, :checked`

- `:has() + :has-text()`

- `shadow:: pierce selectors`

```python
page.selector("form:has(input[name=email]) >> button:visible").click()
```

## 3. [Autowait Engine (Eliminates 95% Flakiness)](https://github.com/pancht/nrobo/blob/production/docs/auto_wait_engine.md)

- Retries

- Scroll into view

- Visibility checks

- Stale element handling

- WebDriverWait on every action

```python
page.selector("#login").click()  # auto-waits
```

## 4. [Locator Collections API](https://github.com/pancht/nrobo/blob/production/docs/locator_collection.md)

```python
rows = page.selector("tr").all()
rows.filter(has_text="Active").first().click()
```

Supports:

- `.all()`

- `.first()`, `.last()`, `.nth(i)`

- `.filter()`

- `.map()`

- set-like operations

## 6. 🔌 [API Testing Support](https://github.com/pancht/nrobo/blob/production/docs/api_testing.md)

## 5. Modern Reporting (HTML + Allure)

- Automatic screenshots

- Logs with timestamps

- Optional built-in Nginx Allure server

## 📦 Installation

```python
pip install nrobo
nrobo init --app my_project
nrobo
```

## 📘 Documentation

- [Architecture Overview](https://github.com/pancht/nrobo/blob/production/docs/architecture_overview.md)

- [Selector Engine](https://github.com/pancht/nrobo/blob/production/docs/selector_engine.md)

- [Locator Chaining](https://github.com/pancht/nrobo/blob/production/docs/locator_action_chaining.md)

- [Locator Collections API](https://github.com/pancht/nrobo/blob/production/docs/locator_collection.md)

- [Autowait engine](https://github.com/pancht/nrobo/blob/production/docs/auto_wait_engine.md)

- Selenium Compatibility Layer

- [Extending nRobo](https://github.com/pancht/nrobo/blob/production/docs/extending_nrobo.md)

  - [Extending selector engine](https://github.com/pancht/nrobo/blob/production/docs/extending_selector_engine.md)
  - [Creating domain specific locators](https://github.com/pancht/nrobo/blob/production/docs/creating_domain_specific_selectors.md)
  -
All inside the `docs/` directory.

## 🧱 Project Structure

```python
nrobo/
  src/nrobo/
  docs/
  suites/
  tests/
```

## 🛠 Developer Guide

```python
black src/ tests/
flake8 src/ tests/
pytest --cov=src/
```

Pull requests welcome!

## MIT License
© 2025 pancht

[//]: # ()
[//]: # (## 📘 Table of Contents)

[//]: # (- Architecture)

[//]: # (- Why nRobo?)

[//]: # (- Features)

[//]: # (- Install & Setup)

[//]: # (- Quick Start)

[//]: # (- Writing Tests)

[//]: # (- Selector Engine)

[//]: # (- Locator Collections)

[//]: # (- AutoWait Engine)

[//]: # (- Reports)

[//]: # (- Contributing)

[//]: # (- License)

[//]: # ()
[//]: # (### Architecture)

[//]: # ()
[//]: # (> ℹ️ See [docs/architecture.md]&#40;docs/architecture.md&#41; for the nRoBo architecture diagram and design details.)

[//]: # (> nRobo is built on a modular architecture with clear separation between loader, executor, selector engine, autowait engine, and reporters.)

[//]: # (>)

[//]: # (### ⭐️ Why nRobo?)

[//]: # (- 🧠 Because Selenium needs modern selectors.)

[//]: # (- ⚙️ Because Playwright's power should work everywhere.)

[//]: # (- 🔥 Because flaky tests waste time — stability should be automatic.)

[//]: # ()
[//]: # (**nRobo** solves all three.)

[//]: # ()
[//]: # (## 🚀 Features)

[//]: # ()
[//]: # (### Exclusive to nRobo)

[//]: # ()
[//]: # (#### Locator Action Chaining)

[//]: # ()
[//]: # (nRobo introduces a Playwright-inspired but Selenium-compatible fluent chaining API that allows:)

[//]: # (- `locator&#40;&#41;.click&#40;&#41;.locator&#40;&#41;.fill&#40;&#41;.should_be_visible&#40;&#41;`)

[//]: # (- Mixed XPath/CSS/Text/Shadow selectors)

[//]: # (- AutoWait on every chained action)

[//]: # ()
[//]: # (This feature is optional and configurable via `settings.ENABLE_LOCATOR_ACTION_CHAINING`.)

[//]: # ()
[//]: # (➡️ **Full Documentation:**  )

[//]: # (See: [docs/locator_action_chaining.md]&#40;docs/locator_action_chaining.md&#41;)

[//]: # ()
[//]: # (### Integration featurea)

[//]: # ()
[//]: # (1. ✅ **PyTest-Powered Engine** – built on the rock-solid `pytest` foundation)

[//]: # (2. 📊 **Allure + HTML Reporting** – customizable test reports with logs and screenshots)

[//]: # (3. 🌀 **Integrated Nginx Allure Server** – serves Allure reports without needing the Allure CLI, and includes simple start, status, and stop commands for hassle-free report hosting)

[//]: # (4. 🖥️ **Selenium Web Integration** – cross-browser support &#40;Chrome, Firefox, Edge&#41;)

[//]: # (5. 🧱 **Modular Architecture** – decoupled loader, executor, and reporter components)

[//]: # (6. 📸 **Screenshots on Failure** - Automatically captures and attaches browser screenshots when a test fails — works with both HTML reports and Allure reports for instant visual debugging.)

[//]: # (7. 🕒 **Logs & Timestamps** - Every test run includes detailed logs with timestamps, durations, and structured formatting — making it easy to trace failures, slow steps, and unexpected behavior.)

[//]: # (8. 📜 **YAML-Based Test Suites** – write tests in a human-readable format)

[//]: # (9. 🧪 **Self-Tested Framework** – internal tests for reliability)

[//]: # (10. 📦 **Modern Packaging** – install via `pip`, structured with `pyproject.toml`)

[//]: # (11. 🛡️ **Security Audited** – integrates with `bandit` and `pip-audit`)

[//]: # (12. ⚙️ **CI/CD Friendly** – GitHub Actions-ready out of the box)

[//]: # (13. 🧠 Powercharged Selenium with the following:)

[//]: # (    1. **Advanced Selector Engine &#40;Playwright-Level&#41;** - Supports everything you know from Playwright — but works on Selenium:)

[//]: # (       - text=Login, "Login", regex /login/i)

[//]: # (       - button:visible, input:enabled, :checked, :not&#40;.disabled&#41;)

[//]: # (       - :has&#40;&#41; nested selectors)

[//]: # (       - :has-text&#40;&#41;)

[//]: # (       - shadow:: pierce selectors &#40;>>>&#41;)

[//]: # (    ```css)

[//]: # (    form:has&#40;input[name=email]&#41; >> button:visible)

[//]: # (    shadow::todo-app >>> li:has-text&#40;"Done"&#41;)

[//]: # (    ```)

[//]: # (    2. 🧩 **Smart Locator & Collection API** - Like Playwright, but runs on Selenium:)

[//]: # (    ```python)

[//]: # (    page.selector&#40;"#email"&#41;.fill&#40;"admin@example.com"&#41;.press&#40;"Enter"&#41;)

[//]: # (    page.selector&#40;"div.card:has&#40;.price&#41;"&#41;.nth&#40;2&#41;.click&#40;&#41;)

[//]: # (    page.selector&#40;"li.item"&#41;.all&#40;&#41;.filter&#40;has_text="Active"&#41;.first&#40;&#41;.click&#40;&#41;)

[//]: # (    ```)

[//]: # (    3. **Collection features:**)

[//]: # (       - .all&#40;&#41;)

[//]: # (       - .first&#40;&#41;, .last&#40;&#41;, .nth&#40;i&#41;)

[//]: # (       - .filter&#40;&#41;, .map&#40;&#41;, .slice&#40;&#41;)

[//]: # (       - Set operations: union, intersection, difference)

[//]: # (       - .random&#40;&#41;)

[//]: # ()
[//]: # (    1. ⚙️ **AutoWait & Stability Engine** - Eliminates 95% of test flakiness:)

[//]: # ()
[//]: # (       - Built-in retries)

[//]: # ()
[//]: # (       - Scroll into view before action)

[//]: # ()
[//]: # (       - Automatic visibility checks)

[//]: # ()
[//]: # (       - Stale element recovery)

[//]: # ()
[//]: # (       - WebDriverWait built into every action)

[//]: # ()
[//]: # (       - No sleeps, no explicit waits needed)

[//]: # ()
[//]: # (       Example:)

[//]: # ()
[//]: # (        ```python)

[//]: # (        page.selector&#40;"#login"&#41;.click&#40;&#41;   # waits automatically)

[//]: # (        page.selector&#40;"#email"&#41;.fill&#40;"user"&#41;)

[//]: # (        ```)

[//]: # ()
[//]: # (    1. 🌐 **Deep Selenium Compatibility Layer**)

[//]: # (       - Works with all WebDrivers &#40;Chrome, Edge, Firefox, Safari&#41;)

[//]: # ()
[//]: # (       - Full WebElement support through __getattr__)

[//]: # ()
[//]: # (       - ActionChains support &#40;hover, drag, double_click&#41;)

[//]: # ()
[//]: # (       - Selenium-based typing &#40;Protocol&#41; ensures autocomplete)

[//]: # ()
[//]: # (       You can always fall back to raw Selenium if needed:)

[//]: # ()
[//]: # (        ```python)

[//]: # (        page.selector&#40;"#submit"&#41;._find&#40;&#41;.get_attribute&#40;"class"&#41;)

[//]: # (        ```)

[//]: # ()
[//]: # (    1. 📚 **Developer Experience & Extensibility**)

[//]: # (       - Clean, modern API design)

[//]: # ()
[//]: # (       - Fully typed &#40;Protocol-based&#41;)

[//]: # ()
[//]: # (       - Modular selector engine &#40;easy to extend&#41;)

[//]: # ()
[//]: # (       - Add your own pseudo selectors)

[//]: # ()
[//]: # (       - Build your own condition helpers)

[//]: # ()
[//]: # (       - Elegant plugin architecture &#40;coming soon&#41;)

[//]: # ()
[//]: # (    1. 🔍 **Example: Complex Selecto**)

[//]: # ()
[//]: # (        Playwright-style selectors on Selenium:)

[//]: # ()
[//]: # (        ```python)

[//]: # (        page.selector&#40;)

[//]: # (            "form:has&#40;input[name=email]&#41; >> button:has-text&#40;'Submit'&#41;:visible")

[//]: # (        &#41;.click&#40;&#41;)

[//]: # (        ```)

[//]: # ()
[//]: # (    1. **Shadow DOM support:**)

[//]: # ()
[//]: # (        ```python)

[//]: # (        page.selector&#40;"shadow::todo-app >>> li:has-text&#40;'Completed'&#41;"&#41;.click&#40;&#41;)

[//]: # (        ```)

[//]: # ()
[//]: # (    1. **Nested filters:**)

[//]: # ()
[//]: # (        ```python)

[//]: # (        rows = page.selector&#40;"tr:visible"&#41;.all&#40;&#41;)

[//]: # (        rows.filter&#40;has_text="Active"&#41;.nth&#40;0&#41;.click&#40;&#41;)

[//]: # (        ```)

[//]: # ()
[//]: # (## 🚀 Upcoming Features)

[//]: # (- 🔧 **Reusable Steps & Configs** – DRY principle applied across suites)

[//]: # (- 🔁 **Data-Driven Testing** – externalize inputs for flexible test coverage)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## 🔥 Feature Comparison)

[//]: # (| Feature                | Selenium    | Playwright  | nRobo |)

[//]: # (| ---------------------- |-------------|-------------|-------|)

[//]: # (| CSS Selectors          | ✅          | ✅          | ✅    |)

[//]: # (| Text Selectors         | ❌          | ✅          | ✅    |)

[//]: # (| has-text&#40;&#41;             | ❌          | ✅          | ✅    |)

[//]: # (| has&#40;&#41;                  | ❌          | ✅          | ✅️    |)

[//]: # (| :visible, :enabled     | ❌          | ✅          | ✅    |)

[//]: # (| Shadow DOM             | ⚠️ limited  | ✅          | ✅    |)

[//]: # (| AutoWait               | ❌          | ✅          | ✅    |)

[//]: # (| Locator Collections    | ❌          | ✅          | ✅    |)

[//]: # (| Selenium Compatibility | ✅          | ❌          | ✅    |)

[//]: # (nRobo = **Playwright power** + **Selenium compatibility**.)

[//]: # ()
[//]: # (## 🧰 Pre-requisites)

[//]: # ()
[//]: # (- Install Python &#40;3.11 or higher&#41;)

[//]: # (  - python --version)

[//]: # ()
[//]: # (## 📦 Installation)

[//]: # ()
[//]: # (### Make a directory for automation project)

[//]: # (```bash)

[//]: # (  mkdir <test_project_name>)

[//]: # (  cd <test_project_name>)

[//]: # (```)

[//]: # (### Install ***venv*** package)

[//]: # (  - 🔵 macOS: No installation needed — macOS Python includes venv.)

[//]: # (  - 🟢 Ubuntu / Debian Linux:)

[//]: # (    - `sudo apt update`)

[//]: # (    - `sudo apt install python3-venv`)

[//]: # (  - 🔶 RedHat / CentOS / Fedora:)

[//]: # (    - `sudo dnf install python3-venv`)

[//]: # (  - 🟣 Windows: No installation needed — Also included by default.)

[//]: # ()
[//]: # (###   Create virtual environment - `.venv`)

[//]: # ()
[//]: # (```bash)

[//]: # (  python -m venv .venv)

[//]: # (```)

[//]: # (### Activate virtual environment)

[//]: # (  - Unix/Mac/Linux)

[//]: # (    - `source .venv/bin/activate`)

[//]: # (  - Windows)

[//]: # (    - `.\\.venv\\Scripts\\activate`)

[//]: # ()
[//]: # (### Install *nrobo*)

[//]: # ()
[//]: # (```bash)

[//]: # (  # Install nrobo)

[//]: # (  pip install nrobo)

[//]: # ()
[//]: # (  # initialize project)

[//]: # (  nrobo init --app <project_name>)

[//]: # ()
[//]: # (  # run sample tests)

[//]: # (  nrobo # This will run sample tests)

[//]: # (```)

[//]: # ()
[//]: # (#### Other ways to work with `nrobo`)

[//]: # (```bash)

[//]: # (    # run tests disabled output capturing)

[//]: # (    # means prints will not be captured and shows up on console right away)

[//]: # (    nrobo -s)

[//]: # ()
[//]: # (    # run 2 tests in parallel with disabled output capturing)

[//]: # (    nrobo -n 2 -s)

[//]: # ()
[//]: # (    # collect tests and show them on console. do not execute them!)

[//]: # (    nrobo --co)

[//]: # (```)

[//]: # ()
[//]: # (#### Example test:)

[//]: # ()
[//]: # (```python)

[//]: # (def test_login&#40;page&#41;:)

[//]: # (    page.selector&#40;"text=Login"&#41;.click&#40;&#41;)

[//]: # (    page.selector&#40;"#email"&#41;.fill&#40;"admin"&#41;)

[//]: # (    page.selector&#40;"#password"&#41;.fill&#40;"secret"&#41;)

[//]: # (    page.selector&#40;"button:has-text&#40;'Login'&#41;"&#41;.click&#40;&#41;)

[//]: # (    page.selector&#40;"text=Welcome"&#41;.should_be_visible&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (#### 🧰 Built-in Helpers)

[//]: # (##### Conditions)

[//]: # ()
[//]: # (```python)

[//]: # (page.selector&#40;"#item"&#41;.should_be_visible&#40;&#41;)

[//]: # (page.selector&#40;"button"&#41;.should_be_enabled&#40;&#41;)

[//]: # (page.selector&#40;"input"&#41;.should_have_text&#40;"Hello"&#41;)

[//]: # (```)

[//]: # ()
[//]: # (##### Collections)

[//]: # ()
[//]: # (```python)

[//]: # (items = page.selector&#40;"li"&#41;.all&#40;&#41;)

[//]: # (assert items.count&#40;&#41; == 5)

[//]: # (```)

[//]: # ()
[//]: # (##### Advanced Operations)

[//]: # (```python)

[//]: # (active = items.filter&#40;has_text="Active"&#41;)

[//]: # (remaining = items.difference&#40;active&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Or** Setup local development environment:)

[//]: # ()
[//]: # (- [On MacOS]&#40;https://github.com/pancht/nrobo/wiki/Local-Development-Setup-&#40;macOS&#41;&#41;)

[//]: # ()
[//]: # ()
[//]: # ()
[//]: # (## 🧪 Quick Start)

[//]: # ()
[//]: # (```bash)

[//]: # (# run login_test test suite only)

[//]: # (nrobo --suite suites/login_test.yaml)

[//]: # (```)

[//]: # ()
[//]: # (## **Or** run via `pytest` if testing a local implementation:)

[//]: # ()
[//]: # (```bash)

[//]: # (nrobo -suite=suites/login_test.yaml)

[//]: # (```)

[//]: # ()
[//]: # (🧱 Directory Structure)

[//]: # ()
[//]: # (```bash)

[//]: # (nrobo/)

[//]: # (├── src/nrobo/         ← Core framework &#40;loader, executor, reporter&#41;)

[//]: # (├── suites/            ← YAML-defined test suites)

[//]: # (├── tests/             ← Unit/integration tests for framework)

[//]: # (├── docs/              ← Architecture docs, diagrams, examples)

[//]: # (├── pyproject.toml     ← Packaging configuration)

[//]: # (└── build_and_publish.py)

[//]: # (```)

[//]: # ()
[//]: # (# 📊 Reports)

[//]: # ()
[//]: # (After execution, nrobo will generate html and allure report through integrated **pytest-html** and **pytest-allure** plugins.)

[//]: # (nRobo will share following in console:)

[//]: # (1. Link of html report)

[//]: # (2. Link of allure report)

[//]: # (3. Sets up local nginx server, and serve allure report for visualization with localhost url.)

[//]: # ()
[//]: # (![img.png]&#40;images/img.png&#41;)

[//]: # ()
[//]: # (🛠️ Developer Guide)

[//]: # ()
[//]: # (Run code checks:)

[//]: # ()
[//]: # (```bash)

[//]: # (black src/ tests/)

[//]: # (flake8 src/ tests/)

[//]: # (pytest --cov=src/)

[//]: # (```)

[//]: # ()
[//]: # (📚 Documentation)

[//]: # ()
[//]: # (- Getting Started)

[//]: # (- Writing Test Suites)

[//]: # (- Architecture Diagram)

[//]: # (- Extending nrobo)

[//]: # ()
[//]: # (👥 Contributing)

[//]: # ()
[//]: # (Want to add your own modules or reporters? Open a pull request or start a discussion!)

[//]: # ()
[//]: # (- Fork this repo)

[//]: # ()
[//]: # (- Create a feature branch)

[//]: # ()
[//]: # (- Add tests for new logic)

[//]: # ()
[//]: # (- Run `black`, `flake8`, and `pytest`)

[//]: # ()
[//]: # (- Submit your PR with a detailed description)

[//]: # ()
[//]: # (📝 License)

[//]: # (MIT © 2025 pancht)
