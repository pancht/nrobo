# 🔌 Extending nRobo
## Build Your Own Selectors, Conditions, Components, Mixins, Reporters & Plugins

nRobo is designed from the ground up to be **modular, extensible, and developer-friendly**.
This document explains how to extend nRobo safely without disrupting core behavior.

## 📘 Table of Contents

1. Philosophy of Extensibility

2. Adding New Pseudo Selectors

3. Adding New Locator Types

4. Adding Custom Actions to Locators

5. Extending AutoWait Engine

6. Writing Custom Mixins

7. Creating Custom Reporters

8. Adding Project-Level Overrides

8. Plugin Architecture (Future Roadmap)

9. Best Practices

## 1. 🧠 Philosophy of Extensibility

nRobo is built around the idea that **everything should be overridable** but **nothing should be fragile**.

Core principles:

- **Stateless locators** → safe to extend

- **Selector Engine registry** → add new pseudo-selectors

- **AutoWait middleware** → insert your own wait rules

- **Protocol-based typing** → scalability without tight coupling

- **Mixins** → use inheritance for optional behaviors

- **Reporter Hooks** → plug into test lifecycle

This separation ensures you can add powerful custom features without modifying core logic.

## 2. 🧩 Adding New Pseudo Selectors
Example: Add `:starts-with(text)` pseudo selector

Pseudo selectors are resolved inside the Selector Engine.

Create a file:

```bash
src/nrobo/extensions/pseudo_startswith.py
```

```python
import re
from nrobo.locators.locator_classifier import register_pseudo

@register_pseudo(":starts-with(")
def handle_startswith(selector: str):
    # extract value from :starts-with("Login")
    text = re.findall(r'starts-with\("(.*)"\)', selector)[0]
    return ("PSEUDO", {"type": "starts-with", "value": text})
```

Then use it in test:

```python
page.selector("button:starts-with('Log')").click()
```

**Without modifying framework core**

Because nRobo automatically loads registered pseudo rules from the extension registry.

## 3. 🧬 Adding New Locator Types

You can extend the `LocatorClassifier` to detect new selector kinds.

Example: Add `role=button` style selectors:

```bash
src/nrobo/extensions/role_locator.py
```

```python
from nrobo.locators.locator_classifier import register_locator_type, LocatorType

@register_locator_type("role=")
def detect_role(locator: str):
    if locator.startswith("role="):
        return LocatorType.ROLE
```

Then extend SeleniumWrapper to handle `ROLE`:

```python
def _find_by_role(self, locator):
    role = locator.value
    return self.driver.find_element(By.CSS_SELECTOR, f"[role='{role}']")
```


# 4. 🖱️ Adding Custom Locator Actions

You can augment Locator with custom behaviors.

Example: `locator().double_click()`:

```bash
src/nrobo/extensions/double_click.py
```

```python
from selenium.webdriver import ActionChains
from nrobo.locators.locator import Locator

def double_click(self: Locator):
    el = self._find()
    ActionChains(self.wrapper.driver).double_click(el).perform()
    return self._maybe_chain()

Locator.double_click = double_click
```


Usage:

```python
page.selector("#menu").double_click()
```

## 5. ⚙️ Extending AutoWait Engine

AutoWait rules live inside `AutoWaitMixin`.

You can override or inject custom logic:

```python
from nrobo.mixins.autowait_mixin import AutoWaitMixin

class CustomAutoWait(AutoWaitMixin):
    def before_action(self, locator):
        super().before_action(locator)
        # enforce custom wait rule
        self.wait_for_network_idle()

    def wait_for_network_idle(self):
        # example placeholder
        pass
```

Then create a custom SeleniumWrapper:

```python
class CustomWrapper(CustomAutoWait, SeleniumWrapper):
    pass
```


Configure via:

```python
settings.SELENIUM_WRAPPER_CLASS = CustomWrapper
```

## 6. 🧩 Writing Custom Mixins

Mixins allow you to add optional functionality.

Example: Add `scroll_to_bottom()`:

```python
class ScrollMixin:
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
```

Combine with SeleniumWrapper:

```python
class CustomWrapper(ScrollMixin, SeleniumWrapper):
    pass
```

## 7. 📊 Creating Custom Reporters

You can hook into:

- test start

- test finish

- step executed

- error captured

- screenshot events

Example reporter:

```python
class SlackReporter:
    def on_test_end(self, test, result):
        if result.failed:
            send_slack_message(f"Test failed: {test.name}")
```

Register it:

```python
settings.REPORTER_CLASSES.append("nrobo.extensions.slack_reporter.SlackReporter")
```


## 8. 🛠️ Adding Project-Level Overrides

Users may want local overrides without touching framework code.

Create a directory:

```bash
project_root/nrobo_overrides/
```

Inside:

- custom selector rules

- custom reporter

- wrapper override

Set:

```ini
settings.EXTENSION_MODULES = ["nrobo_overrides"]
```


nRobo auto-imports everything inside.

## 9. 🔌 Plugin Architecture (Future Roadmap)

Upcoming plugin system will support:

- Plugin discovery (`entry_points`)

- Built-in plugin registry

- On-demand enabling/disabling

- Namespaced plugin commands (e.g., `nrobo plugins list`)

- Marketplace for community extensions

Planned plugin types:

- Selector plugins

- AutoWait plugins

- Reporter plugins

- Debugger plugins

- Cross-browser support plugins

- Visual testing plugins

## 10. 🧭 Best Practices for Extending nRobo
### ✔ Do

- Keep extensions in separate modules

- Use mixins to avoid inheritance conflict

- Register new selector logic instead of patching core

- Write tests for custom rules

- Maintain compatibility with SeleniumWrapper

### ❌ Avoid

- Monkey-patching Locator internals

- Overwriting core selector behavior unless necessary

- Tight coupling to Selenium private APIs

### 🟢 Recommended

- Prefix custom selectors: :myapp-visible, role=, etc.

- Use the chain semantics properly (locator().click().fill())

- Contribute stable extensions back to the repo

## 🎉 Summary

nRobo was designed to grow with your project.

This extensibility ecosystem allows you to:

- Add new selector patterns

- Add new locator types

- Add new actions

- Add or modify AutoWait rules

- Build custom reporters

- Implement mixins for custom automation behaviors

- Override large parts of the framework without forking

Whether you're building domain-specific selectors, enterprise plugins, or CI-level integrations — nRobo makes it straightforward, clean, and maintainable.
