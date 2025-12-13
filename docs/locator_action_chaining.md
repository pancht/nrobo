# nRobo Exclusive Feature: Locator Action Chaining
## A Unified, Fluent, Playwright-Inspired Action API for Selenium

Traditional Selenium APIs require users to break interactions into multiple steps:
```python
driver.find_element(By.CSS_SELECTOR, "a[href='/login']").click()
driver.find_element(By.CSS_SELECTOR, "#username").send_keys("admin")
driver.find_element(By.CSS_SELECTOR, "#password").send_keys("secret")
```

Playwright introduced a more fluent style:
```python
page.locator("a[href='/login']").click()
page.locator("#username").fill("admin")
```

**nRobo extends this concept with an exclusive innovation:
Locator Action Chaining.**

It allows logical, human-readable, multi-step interactions in one continuous chain—without losing clarity, power, or compatibility with Selenium under the hood.

### What is Locator Action Chaining?

With chaining enabled:
```python
page.locator("a[href='/add_remove_elements/']").click() \
    .locator("#content > div > button")
    .should_be_visible()
    .click()
```

This works because **every action method returns the same Locator object** (or None, when disabled), enabling you to keep chaining further actions or locators.

This provides:

- Cleaner syntax

- Readable test intent

- Less repetition of variable names

- Playwright-style fluidity

- Selenium’s reliability with AutoWait built in


### How to Enable or Disable Action Chaining

In your settings.py:
```python
ENABLE_LOCATOR_ACTION_CHAINING = True   # Enable chaining
# ENABLE_LOCATOR_ACTION_CHAINING = False  # Disable chaining (explicit style)
```

When disabled, calls behave just like Selenium:
```python
page.locator("button").click()   # returns None
```

When enabled:
```python
page.locator("button").click().should_be_visible()
```


### Why This Feature Is Unique

Playwright allows chaining ***new locators***:
```python
page.locator("div").locator("span").click()
```

But **Playwright does NOT allow chaining actions back into locators** (e.g. click().locator(...)).

Selenium also does not support any native chaining syntax.

**nRobo introduces the world’s first hybrid model:**

| Capability                                               | Selenium                   | Playwright | nRobo                                 |
| -------------------------------------------------------- | -------------------------- | ---------- | ------------------------------------- |
| Locator-to-Locator chaining (`locator().locator()`)      | No                         | Yes        | Yes                                   |
| Action chaining (`click().fill().press()`)               | No                         | No         | **Yes (optional)**                    |
| Mixed chaining (`click().locator().should_be_visible()`) | No                         | No         | **Yes**                               |
| AutoWait on every action                                 | No (manual waits required) | Yes        | Yes                                   |
| Shadow DOM selectors (`>>>`)                             | No                         | Yes        | Yes                                   |
| Unified XPath/CSS/Text selector engine                   | No                         | Yes        | **Yes (Selenium + Playwright style)** |
| nth(), first(), last() locators                          | No                         | Yes        | Yes                                   |
| has(), has_text(), pseudo selectors                      | No                         | Yes        | **Yes**                               |
| Works fully on Selenium WebDriver                        | N/A                        | No         | **Yes**                               |
| Fully pluggable & controllable via settings              | No                         | No         | **Yes**                               |


### Why Testers Love This Feature
1. Cleaner Tests

You write fewer lines while expressing more intent.

2. No Mental Context Switching

Selenium users gain Playwright’s ergonomics without leaving WebDriver.

3. Optional

Teams can enable/disable chaining based on preference.

4. Zero Learning Curve

Follows natural English-like test flow:
```python
page.locator("input#email")
    .click()
    .fill("tester@example.com")
    .should_have_value("tester@example.com")
```

5. Powerful with Playwright-Style Selectors

Works with:

- `text=Login`

- `role=button`

- `div >> span`

- `:visible`

- `:has-text("Email")`

- XPath, CSS, Shadow DOM

All inside the same chained flow.

### Examples

#### Example 1 — Fluent Form Submission
```python
page.locator("text=Login").click() \
    .locator("#username").fill("admin") \
    .locator("#password").fill("secret") \
    .locator("button[type='submit']").click() \
    .locator("text=Dashboard").should_be_visible()
```

#### Example 2 — XPath + CSS + Pseudo Selector Hybrid
```python
page.locator("//form").locator(":visible").locator("input[name='q']").fill("nrobo")
```

### Summary

nRobo’s **Locator Action Chaining** blends the best ideas from Selenium and Playwright into a single, fluent API that is:

- Optional

- Predictable

- Backward compatible

- Highly expressive

- Extremely readable

- Built for real-world automation frameworks

It is one of the **signature differentiators** of nRobo.
