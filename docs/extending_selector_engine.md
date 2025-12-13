# 🧩 Extending the Selector Engine
## How to Add Custom Selectors, Pseudo Selectors, Filter Logic, and Smart Locator Behaviors

The **Selector Engine** is one of the most powerful components of nRobo.
It brings Playwright-level selector superpowers to Selenium while keeping everything fully extensible.

This document explains how to **extend** the selector engine without modifying core framework code.

# 📘 Table of Contents

1. Overview of the Selector Engine

2. Internal Architecture

3. Adding New Pseudo Selectors

4. Adding Nested Selectors (:has(), etc.)

5. Adding New Locator Types

6. Extending Regex/Text Selectors

7. Overriding Selector Precedence Rules

8. Adding Custom Chaining Behavior

9. Extension Loading Mechanism

10. Best Practices

## 1. 🔍 Overview of the Selector Engine

nRobo supports:

- CSS

- XPath

- Text selectors (`text=Login`, `"Login"`, `/login/i`)

- Pseudo selectors (`:visible`, `:enabled`, `:has()`)

- Shadow DOM selectors (`shadow::todo-app >>> li`)

- Hybrid selectors (`form:has(input) >> button:visible`)

- Collections (`all()`, `filter()`, `nth()`, etc.)

Under the hood, the engine is a **chain of resolvers**, each responsible for detecting and transforming a specific selector type.

You can hook into this chain to introduce new selector syntax.

## 2. 🛠️ Internal Architecture

The Selector Engine consists of:

### 1. LocatorClassifier

Detects selector category:

- CSS

- XPath

- Text selector

- Regex

- Pseudo selector

- Shadow selector

- Has-text

- Unknown fallback

You can register new detectors.

### 2. Selector Resolver Pipeline

After classification, nRobo uses:

- _resolve_css

- _resolve_xpath

- _resolve_text

- _resolve_shadow

- _resolve_pseudo

- _resolve_has

- _resolve_has_text

You can inject new resolver functions into this pipeline.

### 3. Locator

The Locator orchestrates chaining and calls resolvers.

### 4. SeleniumWrapper

Executes final lookup:

- _resolve_with(by, value)

- _find_by_text()

- _find_by_pseudo()

- _find_shadow()

You can override these to add new behaviors.

## 3. 🌱 Adding New Pseudo Selectors

Example: Introduce `:starts-with("text")`

Create file:

```bash
src/nrobo/extensions/pseudo_startswith.py
```

Register new pseudo selector:

```python
import re
from nrobo.locators.locator_classifier import register_pseudo

@register_pseudo(":starts-with(")
def resolve_startswith(selector: str):
    # Extract inner value
    match = re.search(r'starts-with\("(.+?)"\)', selector)
    if not match:
        return None
    text = match.group(1)

    return ("PSEUDO", {"type": "starts-with", "value": text})

```

Implement handler inside SeleniumWrapper:

```python
def _find_by_pseudo(self, locator):
    data = locator.value
    if data["type"] == "starts-with":
        return self._find_by_text_prefix(data["value"])
```

Usage:

```python
page.selector("button:starts-with('Log')").click()
```

## 4. 🌳 Extending Nested Selectors (has(), has-text())

You can add your own nested selectors similar to `:has()`.

Example: add `:contains-text("x")`.

```python
from nrobo.locators.locator_classifier import register_nested_selector

@register_nested_selector(":contains-text(")
def resolve_contains_text(selector: str):
    text = selector.split(":contains-text(", 1)[1].rstrip(")")
    return ("HAS_TEXT", text)
```

Now supported:

```python
page.selector("li:contains-text('Active')").click()
```

## 5. 🧬 Adding New Locator Types

Example: Custom data-test selectors → data-test=login

```bash
src/nrobo/extensions/data_test_locator.py
```

```python
from nrobo.locators.locator_classifier import register_locator_type, LocatorType

@register_locator_type("data-test")
def detect_data_test(locator: str):
    if locator.startswith("data-test="):
        name = locator.split("=", 1)[1]
        return LocatorType.CUSTOM, name
```

Extend SeleniumWrapper:

```python
def _find_custom(self, locator):
    value = locator.value
    return self.driver.find_element(By.CSS_SELECTOR, f"[data-test='{value}']")
```

Usage:

```python
page.selector("data-test=login").click()
```

## 6. 🎯 Extending Regex/Text Selectors

Example: Allow `t:Login` shorthand:

```python
from nrobo.locators.locator_classifier import register_text_alias

@register_text_alias("t:")
def detect_shorthand(locator):
    if locator.startswith("t:"):
        return ("TEXT", locator[2:])
```

Example:

```python
page.selector("t:Logout").click()
```

## 7. 🧵 Overriding Selector Precedence Rules

Default resolution order:

1. Shadow

2. XPath

3. Text

4. Has-text

5. Has

6. Pseudo

7. CSS

You may override priority:

```python
settings.SELECTOR_PRECEDENCE = [
    "TEXT",
    "CSS",
    "PSEUDO",
    ...
]
```


nRobo will re-order the resolver pipeline.

## 8. 🔗 Adding Custom Locator Chaining Behavior

Chaining is controlled by:

```python
settings.ENABLE_LOCATOR_ACTION_CHAINING = True/False
```


You can override chain-building logic:

```python
from nrobo.locators.locator import Locator

def custom_chain_logic(self):
    print("Chaining executed!")
    return self

Locator._maybe_chain = custom_chain_logic
```

## 9. 🔌 Extension Loading Mechanism

nRobo auto-loads extension modules defined in:

```python
settings.EXTENSION_MODULES = [
    "nrobo.extensions",
    "project_name.custom_extensions",
]
```


Each module is scanned for:

- `register_pseudo()`

- `register_nested_selector()`

- `register_locator_type()`

- `register_text_alias()`

This allows plug-and-play architecture without modifying core files.

## 10. 🧭 Best Practices
### ✔ DO:

- Keep extensions self-contained

- Write tests for custom selectors

- Prefer pseudo selectors over XPath hacks

- Use simple resolver functions

- Document custom behaviors

### ❌ AVOID:

- Directly modifying LocatorClassifier internals

- Overwriting core handlers unless required

- Creating circular selectors (infinite recursion risk)

- Recommended Folder Layout:
```python
nrobo_overrides/
    selectors/
        pseudo_startswith.py
        role_locator.py
    wrappers/
        custom_wrapper.py
    reporters/
        slack_reporter.py
```

Add to settings:

```python
settings.EXTENSION_MODULES.append("nrobo_overrides")
```

## 🎉 Conclusion

nRobo’s Selector Engine is meant to be extended.

You can add:

- ✔ new pseudo selectors
- ✔ new nested selectors
- ✔ new locator types
- ✔ new regex/text modes
- ✔ custom chaining rules
- ✔ custom resolvers

—all without touching framework internals.

This makes nRobo a highly adaptable automation engine for **enterprise, domain-specific, and next-gen test design**.
