# 🏛️ nRobo Architecture Overview
## Modular, Extensible, Playwright-Inspired Selenium Automation Framework

nRobo is built on a **cleanly layered, modular architecture** that separates concerns across execution, selection, waiting, reporting, and CLI orchestration.

This document provides an architectural overview that will help:

- **Users** understand how nRobo achieves stability and expressiveness

- **Contributors** understand where to extend or modify subsystems

- **Integrators** plug nRobo into CI/CD, custom selectors, shadow engines, or reporting pipelines

## 📘 Table of Contents

1. High-Level Architecture Diagram

2. Execution Flow Overview

3. Core Components

4. Selector Engine Architecture

5. Locator & Collection Architecture

6. AutoWait Engine

7. Reporter Pipeline

8. CLI & Project Layout

9. Extensibility Points

10. Component Interaction Summary

## 1. 🧩 High-Level Architecture Diagram

```powershell
┌──────────────────────────────────────────────────────────┐
│                         CLI / Runner                     │
│                  (nrobo, pytest plugin)                  │
└───────────────┬──────────────────────────────────────────┘
                │
         Test Discovery & Loading
                │
┌───────────────▼──────────────────────────────────────────┐
│                    Test Executor                         │
│           (PyTest Integration Layer)                     │
└───────────────┬────────────────┬─────────────────────────┘
                │                │
          Selector Engine   AutoWait Engine
                │                │
┌───────────────▼────────────────┴─────────────────────────┐
│                         Locator API                      │
│             (Locator, LocatorCollection, nth, filter)    │
└───────────────┬──────────────────────────────────────────┘
                │
         Selenium WebDriver Layer
                │
┌───────────────▼──────────────────────────────────────────┐
│                   Browser Automation                     │
│            (Chrome, Firefox, Edge, Safari)               │
└──────────────────────────────────────────────────────────┘

```

## 2. ⚙️ End-to-End Execution Flow

This describes how nRobo handles a user calling:

```python
page.selector("form:has(input)").click()
```

nRobo performs:

### 1. Locator API invocation
A new Locator instance is created.

### 2. Selector Engine processing
Resolves text selectors, pseudo selectors, CSS/XPath, shadow DOM, regex, has(), etc.

### 3. AutoWait Engine triggers
Ensures:

- element exists

- is visible

- is interactable

- is scrolled into view

- stale recovery

- retries until timeout

### 4. Selenium executes the action
`WebElement.click()` is called safely.

### 5. Reporter pipeline logs the event
Screenshots, HTML/Allure results, logs.

### 6. PyTest aggregates results
Final output delivered to console + reports.

## 3. 🧱 Core Components
### 3.1 SeleniumWrapper

The main compatibility layer between nRobo selectors and Selenium WebDriver.

Responsibilities:

- Resolve locators (`_resolve`, `_resolve_with`, `_resolve_nth`)

- Execute browser interactions

- Enforce AutoWait rules

Provide WebElement-like behavior

### 3.2 Locator

Represents a single selector instance.

Capabilities:

- Compute full selector chain

- Store `by/value` pair

- Provide Playwright-style fluent chaining

- `click()`, `fill()`, `press()`, `assertions` (should_be_visible())

Delegate real element resolution to SeleniumWrapper

### 3.3 LocatorCollection

Represents multiple elements matching a selector.

Capabilities:

- `.all()`

- `.first()`, `.last()`, `.nth()`

- `.filter(has_text=...)`, `.map()`, `.slice()`, `.random()`

- Maintain selector chain semantics

- AutoWait applied on each resolution

### 3.4 AutoWait Engine

A stability layer that ensures all interactions are safe, predictable, and retryable.

Features:

- Implicit waiting

- Visibility & enabled checks

- Scroll into view

- Interception detection

- Stale element recovery

- Exception-safe retry loop

Equivalent to Playwright’s auto-waiting — built on Selenium.

### 4. 🔍 Selector Engine Architecture

The Selector Engine is responsible for resolving Playwright-style selectors.

**Responsibilities**

#### 1. Selector Type Detection

- CSS

- XPath

- text= selectors

- quoted text

- regex

- pseudo selectors (`:visible`, `:checked`, `:has()`)

- shadow DOM (`shadow::`, `>>>`)

- nested selectors

#### 2. Locator Type Classification
Via `LocatorClassifier`:

```css
CSS
XPATH
TEXT
HAS
HAS_TEXT
PSEUDO
JS_TEXT
SHADOW
```

#### 3. Selector Chain Resolution
Combining CSS/XPath/shadow selectors into `full_selector`.

#### 4. Playwright → Selenium translation
Ensures powerful selectors remain Selenium-compatible.

## 5. 🧬 Locator & Collection Architecture
```csharp
Locator
 ├── full_selector
 ├── by/value (pre-resolved)
 ├── parent chain
 ├── index (for nth(), all())
 └── action API (click, fill, assertions)

LocatorCollection
 ├── list[Locator]
 ├── filter(), map(), random()
 └── nth(), first(), last()

```


Design advantages:

- Avoids stale references

- Stateless selector evaluation

- Predictable chain behavior

- Maximum flexibility for users

## 6. ⚙️ AutoWait Engine

AutoWait acts as a middleware between the Locator layer and Selenium.

### AutoWait Responsibilities

- Wait until the element exists

- Wait until visible

- Retry on stale or intercepted clicks

- Perform scroll-into-view

- Wrap every Selenium call with retry logic

- Enforce timeouts

No sleeps. No manual waits. No flakiness.

### Internal Steps

1. Resolve the element

2. Validate interactability

3. Attempt the action

4. On failure → recover + retry

5. On success → continue

## 7. 📝 Reporter Pipeline

nRobo provides:

- HTML Reporter

- Allure Reporter

- Built-in Nginx server for Allure

- Screenshot capture on failure

- Per-step logging

- Test artifact storage

The pipeline:

```css
PyTest → nRobo Reporter → HTML / Allure / Nginx → User
```

Reporters listen to:

- test start/end

- step execution

- failures

- exceptions

- screenshots

## 8. 🖥️ CLI & Project Layout

The nrobo `CLI` orchestrates:

- Test suite selection

- PyTest lifecycle integration

- Parallel execution flags

- Project initialization

- Allure/Nginx server management

### Directory Structure
```bash
src/nrobo/
  core/
  locators/
  selenium_wrappers/
  mixins/
  reporters/
  cli/
  utils/
tests/
docs/
suites/
```


## 9. 🔌 Extensibility Points

nRobo is designed for easy extension.

### Extend Selector Engine

Add new pseudo-selectors (e.g., `:startswith()`, `:endswith()`).

### Extend AutoWait

Add custom wait rules or element heuristics.

### Add Custom Reporters

Implement new output formats or analytics.

### Build Plugins (upcoming)

Pluggable architecture for custom behaviors.

## 10. 🔗 Component Interaction Summary
```sql
Test Script
   ↓
Locator / LocatorCollection
   ↓
Selector Engine
   → resolves selector chain
   ↓
AutoWait Engine
   → ensures safe, stable execution
   ↓
Selenium WebDriver
   → performs browser automation
   ↓
Reporter Pipeline
   → logs, screenshots, reports
   ↓
PyTest
   → aggregates results

```


Core idea:

**Selenium performs the action; nRobo ensures the action is stable, expressive, and safe.**

## 📌 Summary

nRobo delivers:

- Playwright-level selector power

- Selenium-level compatibility

- AutoWait-driven stability

- A modular, extensible architecture

- Predictable and testable component boundaries

This architecture allows nRobo to evolve rapidly while remaining robust and developer-friendly.
