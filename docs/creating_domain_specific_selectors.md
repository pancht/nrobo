# 🏷️ Creating Domain-Specific Selectors
## Build Your Own Business-Level Locator Syntax for nRobo

One of nRobo’s most powerful advantages over Selenium and Playwright is its **pluggable selector architecture**.
You can create **domain-specific selectors (DSLs)** that map business language to UI components.

This allows test cases to read like:

```python
page.selector("crm:lead-status='Qualified'").click()
page.selector("ecom:product-card:has('Add to Cart')").click()
page.selector("bank:account[id='saving']").should_have_text("Active")
```

This is extremely useful for:

- CRM platforms

- Banking/FinTech automation

- E-commerce UIs

- Custom enterprise portals

- Component libraries (Material UI, Bootstrap, Ant, Salesforce LWC, React custom components)

## 📘 Table of Contents

1. What Are Domain-Specific Selectors?

2. Benefits

3. Architecture for DSL Selectors

4. Simple Example: data-test-id Shorthand

5. Business Selector Example: crm:lead-status="Qualified"

6. Component-Based Selector Example: mui:button('Login')

7. E-commerce Example: product:has('Add to Cart')

8. Multi-Part DSL Grammar

9. Making DSL Selectors Chainable

10. Plugging into nRobo

11. Best Practices

12. Test Examples

## 1. 🔍 What Are Domain-Specific Selectors?

A **domain-specific selector** transforms business language into a valid, machine-readable CSS/XPath/Text selector.

Example:

```python
crm:lead-status='Qualified'
```

Becomes:

```python
div.crm-lead-status[data-status='Qualified']
```

All DSLs ultimately resolve to **(by, value)** pairs so Selenium can execute them.

## 2. ⭐ Benefits
### ✔ More readable tests

Instead of brittle CSS:

```python
page.selector("table tbody tr td:nth-child(4)[data-value='Qualified']").click()
```

Use business terminology:

```python
page.selector("crm:lead-status='Qualified'").click()
```

### ✔ Stable under UI redesign

DSLs map to component attributes that rarely change.

### ✔ Works everywhere Selenium works

No dependency on Playwright, no browser constraints.

## 3. 🛠 Architecture for DSL Selectors

nRobo’s selector engine uses:

- `LocatorClassifier` → detect DSL

- `Resolver` → convert DSL → (by, value)

- `Wrapper` → execute element lookup

You extend nRobo by registering:

```python
register_locator_type()
```

Example:

```python
from nrobo.locators.locator_classifier import register_locator_type

@register_locator_type("crm")
def detect_crm(locator: str):
    return "CRM" if locator.startswith("crm:") else None
```

## 4. 🌱 Simple Example: tid=login-button
### Step 1: Create extension file

```python
src/nrobo/extensions/data_test_id.py
```

```python
from nrobo.locators.locator_classifier import register_locator_type, LocatorType

@register_locator_type("tid")
def detect_test_id(locator: str):
    if locator.startswith("tid="):
        return LocatorType.CUSTOM
```

### Step 2: Add resolver in SeleniumWrapper
```python
def _find_custom(self, locator):
    if locator.selector.startswith("tid="):
        value = locator.selector.split("=",1)[1]
        return self.driver.find_element(
            By.CSS_SELECTOR, f"[data-test-id='{value}']"
        )
```

Usage
```python
page.selector("tid=login-button").click()
```

## 5. 🏢 Business Selector Example: CRM Lead Status
### DSL
```css
crm:lead-status="Qualified"
```

### Convert to CSS
```css
div.crm-lead[data-status="Qualified"]
```

### Step 1 – Classifier
```python
@register_locator_type("crm")
def detect_crm(locator):
    if locator.startswith("crm:"):
        return "CRM"
```

### Step 2 – Resolver
```python
def _resolve_crm(self, locator):
    key, value = locator.selector.split("=",1)
    field = key.split(":",1)[1]     # lead-status
    value = value.strip("\"'")      # Qualified

    css = f"[data-crm-{field}='{value}']"
    return ("css selector", css)
```

Usage

```python
page.selector('crm:lead-status="Qualified"').click()
```

## 6. 🎨 Component-Based Selector Example
### Material UI (MUI) Button DSL
```css
mui:button("Login")
```

Translate to:
```css
button.MuiButton-root:has-text("Login")
```

### Classifier
```python
@register_locator_type("mui")
def detect_mui(locator):
    return "MUI" if locator.startswith("mui:") else None
```

### Resolver
```python
def _resolve_mui(self, locator):
    expr = locator.selector  # mui:button("Login")

    if expr.startswith("mui:button"):
        label = expr.split("(",1)[1].rstrip(")").strip("\"'")
        css = f"button.MuiButton-root:has-text('{label}')"
        return ("CSS", css)
```

Usage:
```python
page.selector('mui:button("Login")').click()
```

## 7. 🛒 E-commerce Example
### Product Card DSL
```css
product:has('Add to Cart')
```

Resolve to:

```css
div.product-card:has(button:has-text('Add to Cart'))
```

## 8. 🧩 Multi-Part DSL Grammar

You can build richer grammars like:

```css
crm:lead(status="Qualified", region="EU")
```

Implementation example:

```python
import re

pattern = r"crm:lead\((.+)\)"

@register_locator_type("crm")
def detect_crm(locator):
    return "CRM" if re.match(pattern, locator) else None


def _resolve_crm(self, locator):
    inside = re.match(pattern, locator.selector).group(1)
    parts = dict(kv.split("=") for kv in inside.split(","))

    css = "div.crm-lead" + "".join(
        f"[data-{k.strip()}={v.strip()}]" for k,v in parts.items()
    )
    return ("CSS", css)
```

Usage:
```python
page.selector('crm:lead(status="Qualified", region="EU")').click()
```

## 9. 🔗 Making DSL Selectors Support Chaining

Chaining works automatically because locator chaining resolves only at execution time:

```python
page.selector("crm:lead='Qualified'") \
    .locator("button:has-text('Open')") \
    .click()
```

Nothing extra required.

## 10. 🔌 Plugging Into nRobo

Add your extension package in settings:

```python
settings.EXTENSION_MODULES = [
    "nrobo.extensions",
    "project.custom_selectors",
]
```

nRobo auto-imports all files and registers:

- locator types

- pseudo selectors

- has/has-text extensions

- text aliases

## 11. 📏 Best Practices

### ✔ Design DSLs around stable attributes (data-*, component names).
### ✔ Avoid brittle CSS combinators.
### ✔ Keep selector grammar intuitive.
### ✔ Provide fallbacks for missing attributes.
### ✔ Always write unit tests for DSLs.
### ✔ Support optional parameters (e.g., region, type).

## 12. 🧪 Test Examples
```python
def test_crm_lead_status(page):
    page.selector("crm:lead-status='Qualified'").should_be_visible()


def test_mui_button(page):
    page.selector('mui:button("Login")').click()


def test_product_card(page):
    page.selector("product:has('Add to Cart')").first().click()
```

## 🎉 Conclusion

nRobo allows you to build your own business-level selector language on top of Selenium:

- readable

- stable

- maintainable

- reusable

- expressive

With domain-specific selectors, your tests communicate **intent**, not CSS mechanics.
