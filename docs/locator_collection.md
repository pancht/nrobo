# 📘 Locator Collections in nRobo
## Playwright-Style Collections — Powered by Selenium

nRobo introduces a **first-class LocatorCollection API** that brings Playwright-level power and expressiveness into Selenium automation.
Collections allow you to work with **multiple elements at once**, filter them, pick specific items, perform set operations, and write readable, stable UI tests.

This document covers:

- What collections are

- When they are created

- How they support filtering, slicing, mapping, set operations

- How they integrate with AutoWait and chaining

- Examples for real web applications

## 🧠 What is a Locator Collection?

Whenever you call `.all()` on a Locator:

```python
rows = page.selector("tr").all()
```

You get a `LocatorCollection` object — a list-like container of Locator objects.

Each element in the collection:

- Has its own index

- Respects the parent selector chain

- Is lazily resolved (AutoWait applies on use, not on creation)

Example:

```python
rows[0].click()
rows.first().should_have_text("Active")
rows.last().should_be_visible()
```

## 🔍 How Collections Are Built

A Locator represents a ***single*** logical selector.

A LocatorCollection represents ***many*** elements found by that selector.

Example:

```python
buttons = page.selector("button").all()
```

Internally:

- nRobo uses the selector engine to find all matching elements

- Wraps each into a Locator

- Annotates each Locator with:

  - `.index`

  - `.by`

  - `.value`

  - full chained `.full_selector`

## 🧱 Basic Operations
### 1. `.count()`

Returns number of matching elements.

```python
assert page.selector("li").count() == 5
```

### 2. `.first()`

Returns first element.

```python
first = page.selector("li").first()
first.click()
```

### 3. `.last()`

Returns last element.

```python
page.selector("li").last().should_have_text("Completed")
```

### 4. `.nth(index)`

Returns element at position index.
```python
page.selector("li").nth(2).click()
```

### 5. Index access (`collection[i]`)

Same as `.nth(i)`.

```python
third = page.selector("li").all()[2]
third.should_contain_text("Item 3")
```

## 🎯 Filtering Elements

nRobo includes Playwright-style filtering:

```python
rows = page.selector("tr").all().filter(has_text="Active")
```

Supported filters:

| Parameter                          | Meaning                 |
| ---------------------------------- | ----------------------- |
| `has_text="Login"`                 | Must contain text       |
| `has_not_text="Error"`             | Must not contain text   |
| `has_attribute=("role", "button")` | Attribute must match    |
| `has_regex=r"User \d+"`            | Text must match regex   |
| `has=lambda el: custom_logic(el)`  | Arbitrary custom filter |


### Examples
#### Filter by text
```python
active_rows = rows.filter(has_text="Active")
```

#### Exclude rows
```python
non_error = rows.filter(has_not_text="Error")
```

#### Filter by attribute
```python
buttons = page.selector("button").all().filter(has_attribute=("type", "submit"))
```

#### Filter by regex
```python
users = rows.filter(has_regex=r"User \d+")
```

#### Custom filter
```python
even_rows = rows.filter(has=lambda el: int(el.text.split()[1]) % 2 == 0)
```

## 🔁 First & Last Filtered
### `.first_filtered()`

Returns the first element after applying filters.

```python
row = rows.first_filtered(has_text="Active")
```

### `.last_filtered()`

Returns the last filtered match.

```python
row = rows.last_filtered(has_text="Active")
```

## 🔄 Set Operations for Collections (***Proposed!***)

nRobo supports true set-like operations for LocatorCollection objects.

### 1. `.union`(other)

Return combined unique elements.

```python
all_items = active.union(inactive)
```

### 2. `.intersection`(other)

Return elements present in both.

```python
common = new_items.intersection(old_items)
```

### 3. `.difference`(other)

Return elements present in self but not in other.

```python
remaining = all_items.difference(completed)
```

### 4. `.symmetric_difference`(other)

Return elements that differ between two sets.

```python
updated = old_items.symmetric_difference(new_items)
```


## 🧩 Mapping & Transforming (***Proposed!***)
### `.map`(func)

Apply a function to each element in the collection.

```python
texts = rows.map(lambda loc: loc.text)
assert "Active" in texts
```

### `.slice(start, end)`

Return sub-collection like list slicing.

```python
mid_items = rows.slice(2, 5)
```

## 🌀 Random Element Selection

Useful for fuzzing or random UI verification.

### `.random()`

```python
page.selector("li").all().random().click()
```

## 🧬 Chaining with Collections

Collections retain the parent chain and full selector logic.

Example:

```python
cards = page.selector("div.card").all()

cards
    .filter(has_text="Premium")
    .nth(0)
    .locator("button:visible")
    .click()
```

This works even with:

- has()

- nested selectors

- shadow DOM chains

Because each Locator in the collection retains:

- parent chain

- selector type (CSS / XPath / TEXT / SHADOW)

- index and value resolution

## ⚡ AutoWait Behavior

AutoWait applies to:

- Any action on an element in the collection

- The `.nth()` resolution

- Assertions such as `.should_be_visible()`

Example:

```python
rows.filter(has_text="Active").nth(0).click()
```

AutoWait ensures:

- Visibility

- Interactability

- Scroll into view

- Stale recovery

No sleeps. No explicit waits.


## 🌐 Real-World Examples
### 1. Table Rows Selection
```python
rows = page.selector("tr.data-row").all()

active = rows.filter(has_text="Active")
active.first().click()
```

### 2. Shopping Cart with Dynamic Rows
```python
items = page.selector(".cart-item").all()

expensive = items.filter(has_regex=r"\$\d{3,}")
expensive.last().locator("button.remove").click()
```

### 3. Shadow DOM Collection

```python
todos = page.selector("shadow::todo-app >>> li").all()
todos.filter(has_text="Completed").first().click()
```


## 📝 Best Practices for Collections
### ✔ Use `.filter()` instead of complex CSS

Better readability and stability.

### ✔ Use `.first()` instead of `[0]`

Clear intent + AutoWait included.

## ✔ Use `.map()` for collecting text or attributes

Lower flakiness than direct Selenium calls.

### ✔ Use set operations for complex UIs

Useful for state transitions and list comparisons.


## 📚 Summary

nRobo LocatorCollections provide:

- Playwright-like list manipulation

- Set operations

- Filtering by text, attributes, regex, or custom functions

- AutoWait support

- Full chaining + chain preservation

- Shadow DOM compatibility

- Strong typing and readable API

They transform Selenium from a low-level API into a **high-productivity, expressive automation toolkit.**
