# 📘 nRobo Selector Engine
## Playwright-Level Selectors Running on Selenium

The nRobo Selector Engine brings **modern**, **expressive**, **powerful selectors** to Selenium — including Playwright-style syntax, text selectors, pseudo selectors, shadow DOM piercing, regex filtering, and nested has()/has-text() expressions.

This document explains:

- What selector types nRobo supports

- How chaining, text selectors, regex, pseudo selectors, and shadow piercing work

- Compatibility rules

- Performance characteristics

- Best practices

nRobo transforms Selenium into a **next-generation locator engine** that works reliably across complex apps.

## 🧠 Overview

nRobo introduces multiple selector types:

| Selector Type           | Example                                         | Description                   |
| ----------------------- | ----------------------------------------------- | ----------------------------- |
| **CSS Selectors**       | `#email`, `.btn.primary`                        | Standard Selenium CSS         |
| **XPath Selectors**     | `//div[@class='card']`                          | Fully supported               |
| **Text Selectors**      | `text=Login`                                    | Locate by visible text        |
| **Quoted Text**         | `"Submit"`                                      | Equivalent to text= “Submit”  |
| **Regex Text**          | `/logout/i`                                     | Text matching with regex      |
| **Pseudo Selectors**    | `:visible`, `:enabled`                          | Playwright-style filters      |
| **has()**               | `div:has(button)`                               | Nested conditions             |
| **has-text()**          | `li:has-text("Active")`                         | Text-based filtering          |
| **Shadow DOM**          | `shadow::todo-app >>> li`                       | Piercing shadow roots         |
| **Composite Selectors** | `form:has(input[name=email]) >> button:visible` | Full power of mixed selectors |


Every selector is compatible with:

- AutoWait engine

- Locator chaining

- Locator collections

- Assertions API

- Selenium WebDriver underneath

### 🔍 1. CSS Selectors (Base Level)
CSS remains the default selector type:

```python
page.selector("#email")
page.selector(".btn.primary")
page.selector("ul > li.active")
```


nRobo automatically classifies `#id`, `.class`, `tagname`, and attribute selectors as **CSS**.

### 🔎 2. XPath Selectors

Any selector starting with:

- `//`

- `/`

- `.//`

- `./`

- `..`

- `(//`

- `(/`

- `(@`

…is treated as XPath.

```python
page.selector("//button[@type='submit']")
page.selector(".//div[contains(@class,'card')]")
```

XPath supports chaining:

```python
page.selector("//div").locator("./span")
# Produces: //div//span
```


## 🔤 3. Text Selectors

### A. Explicit `text=` selector

Locate by visible text:

```python
page.selector("text=Login")
page.selector("text=Welcome, User")
```

### B. Quoted string

Equivalent to `text=:`

```python
page.selector("Login")
page.selector("'Submit'")
page.selector('"Cancel"')
```

### C. JS-Text selector (`JS_TEXT`)

For edge cases where plain `text=` fails:

```python
page.selector("/logout/i")
```

Used for regex patterns.


### 🔁 4. Regex Selectors

Supported using `/pattern/`flags syntax:

```python
page.selector("/log.*/i")   # case-insensitive match
```

Used internally by:

- filter(has_regex=...)

- selector with JS_TEXT resolution

## 🎯 5. Pseudo Selectors (Playwright-Style)

Supported pseudo selectors:

| Pseudo           | Description         |
| ---------------- | ------------------- |
| `:visible`       | element is visible  |
| `:enabled`       | not disabled        |
| `:disabled`      | disabled element    |
| `:checked`       | checkbox or radio   |
| `:not(...)`      | negation filter     |
| `:has(...)`      | nested condition    |
| `:has-text(...)` | text inside element |


### Example: visible buttons
```python
page.selector("button:visible")
```

### Combined:
```python
page.selector("input:enabled:not([type=hidden])")
```

## 🌳 6. `has()` **Selector (Nested Structural Conditions)**

Locate an element ***containing*** another element:

```python
page.selector("div:has(button.primary)")
```

Real-world example:

```python
page.selector("form:has(input[name=email]) >> button:visible")
```

Meaning:

- Find `<form>` that contains `<input name=email>`

- Inside that form, find a visible `<button>`

## 📝 7. `has-text()` Selector

Matches text inside the element:

```python
page.selector("li:has-text('Active')")
```

Equivalent collection usage:

```python
items.filter(has_text="Active")
```

## 🌗 8. Shadow DOM Selectors

Pierce through shadow roots using:


| Syntax                  | Meaning                  |
| ----------------------- | ------------------------ |
| `shadow::component-tag` | identifies a shadow host |
| `>>>`                   | shadow root piercing     |


Examples:

```python
page.selector("shadow::todo-app >>> input.new-todo")
```

Chain shadow selectors:

```python
page.selector("shadow::app >>> list >>> li:has-text('Done')")
```

## 🔗 9. Full Selector Chaining Rules

nRobo supports **Playwright-style locator chaining**:

```python
page
  .selector("div.card")
  .locator("button:has-text('Buy')")
  .click()
```

**CSS → CSS**

```python
div.card + button
```

**CSS → Pseudo**
```python
div.card:visible
```

**XPath → XPath**
```python
//div  + ./span  → //div//span
```

**Shadow → Anything**
```python
component >>> button
```

**Mixed Types**

Always resolved using the correct rule automatically:

```python
page.selector("//table").locator("tr:has-text('Active')").first()
```

## 🧬 10. Selector Resolution Priority

When nRobo sees a selector, it classifies it in this order:

1. Shadow DOM (`>>>` or `shadow::`)

2. Text selectors (`text=`, quotes, regex)

3. Playwright pseudo selectors (`:`)

4. `has()` and `has-text()`

5. XPath (`/`, `//`, `./`, `.//`)

6. CSS (fallback default)

This ensures correct interpretation in all cases.


## 🛠 11. Working With Collections

Selector engine integrates with the **LocatorCollection** API:

```python
rows = page.selector("tr:visible").all()

rows.filter(has_text="Active").nth(0).click()

rows.first().should_be_visible()
rows.last().should_have_text("Completed")
```

Supported set-like operations:

```python
active = rows.filter(has_text="Active")
inactive = rows.filter(has_not_text="Active")

remaining = rows.difference(active)
combined = active.union(inactive)
common = active.intersection(other_rows)
```

## ⚡ 12. Performance Notes

Selector Engine is optimized for stability:

- AutoWait wraps every selector resolution

- Visibility and interactability checks are implicit

- Stale element reloads happen automatically

- nRobo resolves only when needed, not on creation

## 🧭 13. Debugging Selectors

Enable verbose logs:

```python
export NROBO_DEBUG_SELECTORS=1
```

You will see:

- Selector classification

- Full chained selector

- Resolved by/value

- Auto-wait retries

## 🧪 14. Best Practices

### ✔ Prefer CSS → fastest
```python
page.selector("#login-button")
```

### ✔ Use text= for stable text matches
```python
page.selector("text=Login")
```

### ✔ Use form:has() for structural testing
```python
page.selector("form:has(input[name=email])")
```

### ✔ Use shadow:: only when needed

Shadow DOM is slower.

### ✔ Use chaining for readability
```python
page.selector("div.card").locator("button:visible").click()
```

## 📚 Summary

nRobo’s selector engine combines:

- Selenium compatibility

- Playwright-like power

- AutoWait reliability

- Full chaining

- Shadow DOM access

- Advanced text and regex support

It offers the **most expressive selector system available on Selenium today**.
