# 🏢 Designing Enterprise Selector Grammars
## Architecting Large-Scale, Business-Friendly Selector DSLs for nRobo

Enterprise automation often involves complex UI systems built with:

- React/Angular/Vue

- Salesforce Lightning

- Oracle Fusion

- SAP UI5

- Material UI

- Bootstrap variants

- Custom in-house component libraries

These systems use **components**, **data attributes**, and **business objects** that do not map cleanly to raw CSS/XPath.
nRobo’s selector engine allows you to design **Enterprise Selector Grammars (ESGs)**—custom DSLs that express intent using domain language rather than UI mechanics.

Example ESG:

```python
page.selector("crm:lead(status='Qualified') >> action:open")
```


This guide helps you design robust DSLs that are:

- Readable

- Maintainable

- Extensible

- Predictable

- Backward compatible

- Team-friendly

## 📘 Table of Contents

1. What is an Enterprise Selector Grammar (ESG)?

2. ESG Architecture Principles

3. Designing a Grammar Structure

4. Recommended Syntax Patterns

5. Mapping Grammar to CSS/XPath/Text

6. Handling Multi-Field Business Objects

7. Supporting Component Libraries

8. Supporting Complex UI Trees

9. Chaining, Nesting & Combinators

10. Grammar Registration & Resolution

11. Writing ESG Unit Tests

12. Versioning Your Grammar

13. Best Practices

14. Anti-patterns

15. Templates for New Grammars

## 1. 🔍 What Is an Enterprise Selector Grammar?

An ESG is a **custom selector language** that maps business terms → actual DOM selectors.

Examples:

```vbnet
crm:lead(id="L-2981", status="Open")
sap:button("Submit")
mui:list-item(text="Dashboard")
salesforce:tile(object="Case", field="Status")
```

These become:

```css
div.crm-lead[data-lead-id='L-2981'][data-status='Open']
button.sap-btn:has-text("Submit")
li.MuiListItem-root:has-text("Dashboard")
div.sf-tile[data-sf-object='Case'][data-field='Status']
```

ESGs express what the business means, not how the HTML is structured.

## 2. 🧱 ESG Architecture Principles

A good grammar should:

### ✔ Abstract UI details

CSS classes, shadow hierarchies, and DOM noise must be hidden.

### ✔ Enforce domain vocabulary

Teams must speak the same selector language.

### ✔ Guarantee stability

ESGs should be built on stable attributes: data-*, component tags, object IDs.

### ✔ Support extensibility

You should be able to add new grammar rules without breaking existing tests.

### ✔ Support chaining

ESGs should compose cleanly with other selectors:

```css
crm:lead(status='New') >> action:assign >> button:has-text('Save')
```

## 3. 🧩 Designing a Grammar Structure

Choose a structure that suits your domain.

### Option A: Function Syntax

```bash
crm:lead(id="123", assigned_to="User1")
```

### Option B: Key-Value Syntax
```bash
crm:lead[id='123'][status='New']
```

### Option C: Verb-Noun Syntax
```bash
crm:lead("New") >> action:open
```

### Option D: Pseudo Selector Integration

```bash
crm:lead:has(action='Open')
```

### Option E: Extended Playwright-Like
```bash
crm:lead(status="Qualified") >> button:has-text("Continue")
```

### Recommendation:
Use **function syntax** (`crm:lead(...)`) for enterprise platforms.
Most readable, predictable, and flexible.

## 4. 📑 Recommended Syntax Patterns
### 4.1 Object Selector Grammar
```vbnet
domain:object(attribute="value", ...)
```

Examples:

```css
crm:lead(status="Qualified")
inventory:item(code="SKU-3201")
sap:tile(name="Sales Orders")
```

### 4.2 Action Grammar
```css
action:name(param)
```

Example:

```css
action:open
action:approve("Manager")
```

### 4.3 Component Grammar
```css
mui:button("Submit")
oracle:field(label="Description")
```

### 4.4 Business Relationship Grammar
```css
crm:lead(status="New") >> crm:task(type="FollowUp")
```

You can design as deep as needed.

## 5. 🔁 Mapping Grammar → CSS/XPath/Text

Your selector resolver will parse the DSL and produce a real selector:

Example:

```css
crm:lead(status="Qualified")
```

Parsing:

```python
type = "lead"
attrs = {"status": "Qualified"}
```

Result:

```css
div.crm-lead[data-status="Qualified"]
```

Or for Salesforce:

```css
salesforce:case(number="50091")
```

Result:
```css
one-app-nav-bar-item-root[data-recordid="50091"]
```

Or Oracle Fusion:

```css
fusion:table(row="3")
```

Result:

```css
(//oj-table/oj-table-body-row)[3]
```

## 6. 🧩 Multi-Field Business Object Grammars (Most Common Case)

Typical enterprise objects have many attributes:

```css
crm:lead(id="L-2199", region="EU", owner="Sam")
```

Map all attributes:

```css
div.crm-lead[data-id="L-2199"][data-region="EU"][data-owner="Sam"]
```

Your parser should:

allow any number of attributes

- ignore whitespace

- support quoted/unquoted values

- support nested parentheses

## 7. 🧬 Component Library Integration

Large UIs are built with component frameworks. Example grammars:

### Material UI
```css
mui:dialog(title="Edit Profile")
mui:list-item("Settings")
mui:button:visible("Save")
```

### Salesforce Lightning
```css
sf:input(label="Email")
sf:tile(object="Opportunity", field="Stage")
```

### SAP UI5
```css
sap:button("Submit")
sap:table(row=2)
sap:field(key="CUSTOMER_ID")
```

Each grammar rule maps to a known DOM pattern.

## 8. 🌲 Complex UI Tree Grammars

For deeply nested UIs:

```css
crm:lead(id="L-2091") >> crm:activity(type="Call") >> button:has-text("Open")
```

Or E-commerce:

```css
product[id='P-901'] >> variant[color='Red'] >> size[label='L'] >> action:add-to-cart
```

Use chaining (`>>`) for tree traversal.

## 9. 🔗 Chaining, Nesting & Combinators

Use Playwright-inspired combinators:

### Descendant chain
```css
crm:lead(status="New") >> button:has-text("Open")
```

### Direct child

crm:lead >> > div.section
```python
Conditional selection (has)
crm:lead:has(button:has-text("Assign"))
```

### Negation
```css
crm:lead:not(status="Closed")
```

## 10. 📦 Grammar Registration

Extend `LocatorClassifier`:

```python
@register_locator_type("crm")
def detect_crm(locator):
    return "CRM" if locator.startswith("crm:") else None
```

Add a resolver:

```python
def _resolve_crm(self, locator):
    return ("CSS", crm_to_css(locator.selector))
```

## 11. 🧪 Unit Testing ESGs

Each grammar rule must have:

### ✔ Classification Tests
### ✔ Parsing Tests
### ✔ CSS/XPath generation tests
### ✔ Chain behavior tests
### ✔ Negative tests
### ✔ Escape character tests

Template:

```python
def test_crm_lead_status():
    loc = Locator(page, "crm:lead(status='Open')")
    assert loc.full_selector == "div.crm-lead[data-status='Open']"
```

## 12. 🧭 Versioning Your Grammar

When UIs evolve, grammars must version:

```css
crm:v1:lead(...)
crm:v2:lead(...)
```


Tests should declare version:

```python
page.selector("crm:v2:lead(status='New')")
```

## 13. ✔ Best Practices

- Use `data-*` attributes whenever possible.

- Avoid CSS classes—they change often.

- Keep grammar names short and clear.

- Be explicit with attributes.

- Allow optional parameters.

- Provide meaningful defaults.

- Write a parser that tolerates whitespace.

- Do not break backward compatibility.

## 14. ⚠ Anti-Patterns

Avoid:

- ❌ Using raw CSS inside grammar
- ❌ Grammars that require XPath only
- ❌ Hardcoding fragile class names
- ❌ Overloading too many syntaxes in one rule
- ❌ Business terminology that QA does not understand

Remember: **The grammar must be readable by humans**.

## 15. 📄 Templates for New Grammars
###CRM Object Template
```css
crm:lead(id="X", status="Y")
```

Resolver:

```css
div.crm-lead[data-id='X'][data-status='Y']
```

### E-commerce Product Template
```css
product(id="P-109") >> action:add-to-cart
```

### Workflow Action Template
```css
action:approve("Manager")
```

### Component Template
```css
component:tooltip(text="Info")
```

## 🎉 Conclusion

Enterprise Selector Grammars make automation:

- Business-friendly

- Stable

- Maintainable

- Declarative

- Scalable across teams

With ESGs, nRobo becomes more than a Selenium wrapper — it becomes an **automation language** tailored to your product ecosystem.
