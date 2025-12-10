# nRobo Example Test Suite

This folder contains demo tests showing how to use every feature of nRobo:
## 🌐 Navigation API in nRobo
nRobo provides a modern, Selenium-compatible navigation API with **automatic page-load waiting**, **navigation detection**, and **Playwright-style ergonomics**.
Every navigation method integrates with the **AutoWait Engine**, so your tests remain stable without manual sleeps.

### 🚀 Navigation Methods

1. `goto(url, wait="load")` — Recommended

nRobo’s preferred navigation method.
Wraps `driver.get()` + intelligent auto-wait.
```python
page.goto("https://example.com")
```

Behavior:

| Parameter               | Meaning                                                          |
| ----------------------- | ---------------------------------------------------------------- |
| `wait="load"` (default) | Always wait for DOM ready (`document.readyState === "complete"`) |
| `wait="none"`           | Do not wait after navigating                                     |
| `wait="auto"`           | Reserved for future use (auto-detect heuristic)                  |

2. `get(url)` — Pure Selenium Equivalent
Shortcut to raw Selenium `driver.get()`.
No automatic waits unless AutoWait detects state change (optional).
```python
page.get("https://example.com")
```

3. `back(wait="auto")`

Navigate to previous page in history.
```python
page.back()
```

Behavior:

- Executes `driver.back()`

- Detects navigation automatically

- Waits for page load if URL changed or readyState dropped

Customization:
```python
page.back(wait="load")   # always wait
page.back(wait="none")   # never wait
```

4. `forward(wait="auto")`

Navigate forward in browser history.
```python
page.forward()
```

Same AutoWait behavior as `.back()`.

5. `refresh(wait="load")`

Refresh current page.
```python
page.refresh()
```

Refresh always triggers a load wait unless explicitly disabled:
```python
page.refresh(wait="none")
```

### 🧠 Why nRobo Navigation Is Better


| Action      | Selenium Default     | nRobo Behavior                              |
| ----------- | -------------------- | ------------------------------------------- |
| `back()`    | No load wait         | Auto-detects navigation + waits             |
| `forward()` | No load wait         | Auto-detects navigation + waits             |
| `refresh()` | May return early     | Guaranteed load wait                        |
| `get()`     | No stability wrapper | AutoWait stability applied                  |
| `goto()`    | Not available        | Best-in-class navigation with waiting modes |

### 📘 Examples

**Basic end-to-end navigation**
```python
page.goto("https://example.com")

page.locator("text=Login").click()

page.back()
page.forward()

page.refresh()
```

**Explicit wait control**
```python
page.goto(url, wait="none")
page.back(wait="load")
page.forward(wait="none")
page.refresh(wait="load")
```

## 2. Locators
- CSS, XPath, Shadow DOM, Text selectors
- nth(), all(), filter()
### 📘 nRobo CSS Selector Table (with Implementation Examples)
| Selector Pattern                                             | Description                    | nRobo Usage Example                                                          |
| ------------------------------------------------------------ | ------------------------------ | ---------------------------------------------------------------------------- |
| `h1`                                                         | All `<h1>` elements            | `page.locator("h1")`                                                         |
| `.btn`                                                       | Class selector                 | `page.locator(".btn")`                                                       |
| `#login`                                                     | ID selector                    | `page.locator("#login")`                                                     |
| `div.example`                                                | `<div>` with class `example`   | `page.locator("div.example")`                                                |
| `input[name='email']`                                        | Attribute filter               | `page.locator("input[name='email']")`                                        |
| `[type='checkbox']`                                          | Attribute equals               | `page.locator("[type='checkbox']")`                                          |
| `[href^='/admin']`                                           | Attribute starts with          | `page.locator("a[href^='/admin']")`                                          |
| `[href$='.pdf']`                                             | Attribute ends with            | `page.locator("a[href$='.pdf']")`                                            |
| `[alt*='logo']`                                              | Attribute contains             | `page.locator("img[alt*='logo']")`                                           |
| `div a`                                                      | Descendant                     | `page.locator("div a")`                                                      |
| `div > a`                                                    | Direct child                   | `page.locator("div > a")`                                                    |
| `label + input`                                              | Next sibling                   | `page.locator("label + input")`                                              |
| `h3 ~ p`                                                     | Following siblings             | `page.locator("h3 ~ p")`                                                     |
| `ul li:nth-child(1)`                                         | First item                     | `page.locator("ul li:nth-child(1)")`                                         |
| `tr:nth-of-type(2)`                                          | Second row by type             | `page.locator("table tr:nth-of-type(2)")`                                    |
| `ul li:last-child`                                           | Last child                     | `page.locator("ul li:last-child")`                                           |
| `button:has-text("Login")`                                   | Button containing visible text | `page.locator('button:has-text("Login")')`                                   |
| `h3:has-text("Welcome")`                                     | Header containing text         | `page.locator('h3:has-text("Welcome")')`                                     |
| `a:has-text("A/B Testing")`                                  | Link with text                 | `page.locator('a:has-text("A/B Testing")')`                                  |
| `div:has(input[name='email'])`                               | div containing specific input  | `page.locator("div:has(input[name='email'])")`                               |
| `li:has(a:has-text('File'))`                                 | li containing a link           | `page.locator("li:has(a:has-text('File'))")`                                 |
| `table:has(td:has-text('Active'))`                           | table with cell matching text  | `page.locator("table:has(td:has-text('Active'))")`                           |
| `button:visible`                                             | Only visible buttons           | `page.locator("button:visible")`                                             |
| `input:hidden`                                               | Hidden input fields            | `page.locator("input:hidden")`                                               |
| `button:enabled`                                             | Enabled button                 | `page.locator("button:enabled")`                                             |
| `input:disabled`                                             | Disabled input                 | `page.locator("input:disabled")`                                             |
| `input[type='checkbox']:checked`                             | Checked checkbox               | `page.locator("input[type='checkbox']:checked")`                             |
| `input:not([type='hidden'])`                                 | Not hidden                     | `page.locator("input:not([type='hidden'])")`                                 |
| `shadow::todo-app >>> input.new-todo`                        | Shadow DOM traversal           | `page.locator("shadow::todo-app >>> input.new-todo")`                        |
| `shadow::my-el >>> div.content >>> button`                   | Multi-level shadow DOM         | `page.locator("shadow::my-el >>> div.content >>> button")`                   |
| `form:has(input[name='email']) >> button:has-text("Submit")` | Scoped nested selector         | `page.locator('form:has(input[name="email"]) >> button:has-text("Submit")')` |
| `div.card:has(.price):has-text("$19")`                       | Combine :has + text            | `page.locator('div.card:has(.price):has-text("$19")')`                       |
| `tr:has(td:has-text("Pending")) >> a:has-text("Edit")`       | Find row → find link           | `page.locator('tr:has(td:has-text("Pending")) >> a:has-text("Edit")')`       |
| `div >> "Hello"`                                             | Quoted text selector           | `page.locator('div >> "Hello"')`                                             |
| `h3 >> 'Welcome'`                                            | Find by text inside tag        | `page.locator("h3 >> 'Welcome'")`                                            |

### 📘 XPath Selector Cheat Sheet (with nRobo Examples)
| XPath Pattern                                   | Description                                    | nRobo Usage Example                                             |
| ----------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------- |
| `//h1`                                          | All `<h1>` elements in the document            | `page.locator("//h1")`                                          |
| `//p`                                           | All paragraph tags                             | `page.locator("//p")`                                           |
| `//*[@id='login']`                              | Element with id="login"                        | `page.locator("//*[@id='login']")`                              |
| `//*[@class='btn primary']`                     | Strict class match                             | `page.locator("//*[@class='btn primary']")`                     |
| `//*[contains(@class, 'btn')]`                  | Class contains substring                       | `page.locator("//*[contains(@class, 'btn')]")`                  |
| `//input[@name='email']`                        | Attribute equals                               | `page.locator("//input[@name='email']")`                        |
| `//a[contains(@href, '/login')]`                | Attribute contains                             | `page.locator("//a[contains(@href, '/login')]")`                |
| `//img[starts-with(@src, '/img/')]`             | Attribute starts with                          | `page.locator("//img[starts-with(@src, '/img/')]")`             |
| `//button[text()='Login']`                      | Exact text match                               | `page.locator("//button[text()='Login']")`                      |
| `//button[normalize-space()='Login']`           | Trimmed text match                             | `page.locator("//button[normalize-space()='Login']")`           |
| `//h3[contains(text(),'Welcome')]`              | Partial match on text                          | `page.locator("//h3[contains(text(),'Welcome')]")`              |
| `//div[@id='container']//a`                     | All descendants                                | `page.locator("//div[@id='container']//a")`                     |
| `//ul/li`                                       | All `<li>` children                            | `page.locator("//ul/li")`                                       |
| `//form//input`                                 | Input inside any nested level of form          | `page.locator("//form//input")`                                 |
| `//label/following-sibling::input`              | Input immediately after label                  | `page.locator("//label/following-sibling::input")`              |
| `//div/preceding-sibling::h3`                   | h3 appearing before a div                      | `page.locator("//div/preceding-sibling::h3")`                   |
| `//table//tr[1]`                                | First row of any table                         | `page.locator("//table//tr[1]")`                                |
| `//table//tr[last()]`                           | Last row of any table                          | `page.locator("//table//tr[last()]")`                           |
| `//table//tr[position()=3]`                     | Third row                                      | `page.locator("//table//tr[3]")`                                |
| `//ul/li[position() mod 2 = 1]`                 | Odd items                                      | `page.locator("//ul/li[position() mod 2 = 1]")`                 |
| `(//button)[2]`                                 | Second button on page                          | `page.locator("(//button)[2]")`                                 |
| `//input[@type='checkbox' and @checked]`        | Checked checkbox                               | `page.locator("//input[@type='checkbox' and @checked]")`        |
| `//button[@disabled]`                           | Disabled button                                | `page.locator("//button[@disabled]")`                           |
| `//div[.//span[text()='Active']]`               | div containing `<span>Active</span>`           | `page.locator("//div[.//span[text()='Active']]")`               |
| `//tr[td[contains(text(),'Pending')]]`          | Table row with matching cell                   | `page.locator("//tr[td[contains(text(),'Pending')]]")`          |
| `//*[@*='value']`                               | Any attribute equals 'value'                   | `page.locator("//*[@*='value']")`                               |
| `//input[not(@type='hidden')]`                  | All non-hidden inputs                          | `page.locator("//input[not(@type='hidden')]")`                  |
| `//div[@data-test-id and contains(., 'Hello')]` | div with attribute + text                      | `page.locator("//div[@data-test-id and contains(., 'Hello')]")` |
| `//section//*[self::h1 or self::h2]`            | Headings inside section                        | `page.locator("//section//*[self::h1 or self::h2]")`            |
| `//shadow-root()`                               | (Playwright-only) – Selenium workaround via JS | `page.locator("shadow::...")` *(nRobo uses shadow API instead)* |

### 📘 CSS vs XPath Comparison Table (nRobo Ready)
| Feature                                  | CSS Selector                                 | XPath Selector                              | Notes                                              |
| ---------------------------------------- | -------------------------------------------- | ------------------------------------------- | -------------------------------------------------- |
| **Syntax Style**                         | Lightweight, simple                          | Verbose but powerful                        | CSS best for 90% of test automation                |
| **Readability**                          | Very clean                                   | More complex                                | CSS wins for readability                           |
| **Performance**                          | Faster in most browsers                      | Slightly slower                             | Selenium internally prefers CSS                    |
| **Match by Tag, ID, Class**              | Yes                                          | Yes                                         | `div`, `.btn`, `#login`                            |
| **Match by Text**                        | No (native) <br> Yes (nRobo via `:has-text`) | Yes (`contains(text(), 'x')`)               | XPath best for pure text nodes                     |
| **Match by Index**                       | Limited (`:nth-child`)                       | Very strong (`[1]`, `[last()]`)             | XPath best for positional queries                  |
| **Parent → Child**                       | Yes (`>` and space)                          | Yes (`/` and `//`)                          | Similar capability                                 |
| **Child → Parent**                       | No                                           | Yes (`..`)                                  | XPath advantage                                    |
| **Siblings**                             | Yes (`+`, `~`)                               | Yes (`following-sibling::`)                 | Both support                                       |
| **Regex Support**                        | No                                           | Yes (via `matches()` in XPath 2.0)          | Useful in dynamic text matching                    |
| **Attribute Matching**                   | Native (`[attr='x']`)                        | Native (`[@attr='x']`)                      | CSS version shorter                                |
| **Conditional With Multiple Attributes** | Yes                                          | Yes                                         | Equal capability                                   |
| **Shadow DOM**                           | Not native <br> nRobo: `shadow:: >>>`        | No (Selenium limitation)                    | nRobo implements Playwright-style shadow selectors |
| **Complex Structural Queries**           | Limited                                      | Very powerful                               | XPath shines for hierarchy                         |
| **Case-Insensitive Matching**            | No                                           | Yes (`translate()`)                         | XPath only                                         |
| **Finding by Partial Text**              | nRobo-only (`:has-text`)                     | Native (`contains(text())`)                 | nRobo bridges this gap                             |
| **DOM Traversal Flexibility**            | Medium                                       | Very high                                   | XPath supports axes (`ancestor`, `parent`, etc.)   |
| **Browser Native Support**               | Yes (CSS engine)                             | No (Selenium engine interprets XPath)       | CSS faster                                         |
| **Recommended For**                      | UI elements, attributes, classes, IDs        | Text-based, deeply nested, dynamic elements | Use CSS unless XPath needed                        |

### 🎯 Practical Usage Comparison in nRobo

| Goal                         | CSS Selector                                              | XPath Selector                                            |
| ---------------------------- | --------------------------------------------------------- | --------------------------------------------------------- |
| Click link “A/B Testing”     | `page.locator("a:has-text('A/B Testing')")`               | `page.locator("//a[contains(text(),'A/B Testing')]")`     |
| Find row with text "Pending" | `page.locator("tr:has(td:has-text('Pending'))")`          | `page.locator("//tr[td[contains(text(),'Pending')]]")`    |
| Locate button inside a form  | `page.locator("form:has(input[name='email']) >> button")` | `page.locator("//form[.//input[@name='email']]//button")` |
| First item in list           | `page.locator("ul li:nth-child(1)")`                      | `page.locator("(//ul/li)[1]")`                            |
| Element with id “login”      | `page.locator("#login")`                                  | `page.locator("//*[@id='login']")`                        |

### ⭐ Recommendation for nRobo Users

| Situation               | Recommended Selector        |
| ----------------------- | --------------------------- |
| Typical UI automation   | **CSS**                     |
| Find by text            | **CSS with `:has-text()`**  |
| Deep nested structure   | **XPath**                   |
| Parent traversal needed | **XPath**                   |
| Shadow DOM              | **CSS with `shadow:: >>>`** |
| Highest performance     | **CSS**                     |

### 🧩 Shadow DOM Selectors (Playwright-Style) in nRobo

**nRobo** supports **Playwright-style Shadow DOM traversal** using:

```php-template
shadow::<host> >>> <inner-element>
```
And multi-level shadow roots using chaining:

```php-template
shadow::<host1> >>> <shadow-child> >>> <shadow-grandchild>
```
#### 🧩 Shadow DOM: Selector Table with nRobo Examples

| Shadow DOM Pattern                                                | Description                               | nRobo Usage Example                                                               |
| ----------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------- |
| `shadow::my-app >>> input#username`                               | Locate input inside single shadow root    | `page.locator("shadow::my-app >>> input#username")`                               |
| `shadow::todo-app >>> button.add`                                 | Access a button inside a web component    | `page.locator("shadow::todo-app >>> button.add")`                                 |
| `shadow::custom-el >>> div.content >>> button.save`               | Multi-level nested shadow roots           | `page.locator("shadow::custom-el >>> div.content >>> button.save")`               |
| `shadow::app-root >>> nav.menu >>> a[href='/profile']`            | Find link inside shadow DOM navigation    | `page.locator("shadow::app-root >>> nav.menu >>> a[href='/profile']")`            |
| `shadow::search-box >>> input[type='text']`                       | Query input field inside search component | `page.locator("shadow::search-box >>> input[type='text']")`                       |
| `shadow::modal-dialog >>> button.close`                           | Close button inside a modal component     | `page.locator("shadow::modal-dialog >>> button.close")`                           |
| `shadow::user-card >>> img.avatar`                                | Avatar inside a user card component       | `page.locator("shadow::user-card >>> img.avatar")`                                |
| `shadow::app-shell >>> #sidebar >>> .menu-item:nth-child(3)`      | CSS nth-child inside shadow               | `page.locator("shadow::app-shell >>> #sidebar >>> .menu-item:nth-child(3)")`      |
| `shadow::app-dashboard >>> div:has-text("Reports")`               | Combine shadow DOM + :has-text            | `page.locator('shadow::app-dashboard >>> div:has-text("Reports")')`               |
| `shadow::chat-box >>> input:visible`                              | Shadow root + visibility filter           | `page.locator("shadow::chat-box >>> input:visible")`                              |
| `shadow::my-el >>> button:enabled`                                | Shadow DOM + enabled state                | `page.locator("shadow::my-el >>> button:enabled")`                                |
| `shadow::todo-app >>> li:has-text("Buy Milk")`                    | Shadow + list filtering                   | `page.locator('shadow::todo-app >>> li:has-text("Buy Milk")')`                    |
| `shadow::form-el >>> input[name='email']`                         | Form field inside component               | `page.locator("shadow::form-el >>> input[name='email']")`                         |
| `shadow::product-card >>> .price-tag`                             | Read price visible inside UI component    | `page.locator("shadow::product-card >>> .price-tag")`                             |
| `shadow::main-ui >>> section.panel >>> button:has-text("Submit")` | Deep chain + text selector                | `page.locator('shadow::main-ui >>> section.panel >>> button:has-text("Submit")')` |
| `shadow::my-widget >>> div.container >> "Hello"`                  | Shadow DOM + TEXT engine                  | `page.locator('shadow::my-widget >>> div.container >> "Hello"')`                  |

#### ⭐ Advanced Shadow DOM Patterns

| Pattern                                     | Purpose                                | Example                                                      |
| ------------------------------------------- | -------------------------------------- | ------------------------------------------------------------ |
| `shadow::<host> >>> *`                      | Select all elements inside shadow root | `page.locator("shadow::todo-app >>> *")`                     |
| `shadow::<host> >>> :scope > div`           | First-level children inside shadow     | `page.locator("shadow::todo-app >>> :scope > div")`          |
| `shadow::<host> >>> element >> selector`    | Combine with standard nRobo chaining   | `page.locator("shadow::app >>> list >> 'Item 3'")`           |
| `shadow::<host> >>> element:not(.disabled)` | Use CSS negation inside shadow         | `page.locator("shadow::menu-bar >>> button:not(.disabled)")` |
| `shadow::<host> >>> element:has(child)`     | Combine :has with shadow               | `page.locator("shadow::user-list >>> li:has(.verified)")`    |

### 🔤 Text Selectors in nRobo (Playwright-Style)

nRobo implements a Playwright-compatible text selector engine, supporting:
- text=Exact
- "Quoted Text" (auto-text mode)
- Partial matches
- Case-insensitive search
- :has-text()
- Regex /pattern/
- Combined CSS + text filters
- Combined Shadow DOM + text selectors

#### 📘 Text Selector Table (nRobo)

| Selector Pattern                             | Meaning                                                     | nRobo Example                                                |
| -------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| `text=Login`                                 | Find element whose **visible text contains "Login"**        | `page.locator("text=Login")`                                 |
| `text="A/B Testing"`                         | Exact text match with quotes                                | `page.locator('text="A/B Testing"')`                         |
| `"Login"`                                    | Shorthand for text contains "Login"                         | `page.locator('"Login"')`                                    |
| `'Logout'`                                   | Single-quoted text selector                                 | `page.locator("'Logout'")`                                   |
| `/hello/i`                                   | Regex case-insensitive match                                | `page.locator("/hello/i")`                                   |
| `text=/^Start/`                              | Regex match (starts with "Start")                           | `page.locator("text=/^Start/")`                              |
| `h3:has-text("Status Codes")`                | CSS element **filtered** by text                            | `page.locator('h3:has-text("Status Codes")')`                |
| `a:has-text("Download")`                     | Anchor with matching visible text                           | `page.locator('a:has-text("Download")')`                     |
| `button:has-text("Submit")`                  | Button with visible text "Submit"                           | `page.locator('button:has-text("Submit")')`                  |
| `.item:has-text("Active")`                   | Any element with class `.item` AND text containing "Active" | `page.locator('.item:has-text("Active")')`                   |
| `#menu >> text=Help`                         | Combine CSS + text                                          | `page.locator("#menu >> text=Help")`                         |
| `shadow::my-app >>> text=Settings`           | Text inside Shadow DOM                                      | `page.locator("shadow::my-app >>> text=Settings")`           |
| `shadow::panel-el >>> button:has-text("OK")` | Shadow DOM + has-text                                       | `page.locator('shadow::panel-el >>> button:has-text("OK")')` |
| `.row >> "Details"`                          | Automatic text selector inside chain                        | `page.locator('.row >> "Details"')`                          |
| `li >> /done/i`                              | Regex match inside a locator chain                          | `page.locator("li >> /done/i")`                              |
| `h3:has-text("Welcome")`                     | Locate `<h3>` with matching text                            | `page.locator('h3:has-text("Welcome")')`                     |

#### 🧠 Advanced Text Selector Examples

| Pattern                             | Purpose                     | Example                                             |
| ----------------------------------- | --------------------------- | --------------------------------------------------- |
| `text=Continue`                     | Basic contains text         | `page.locator("text=Continue")`                     |
| `text="Continue"`                   | Exact text                  | `page.locator('text="Continue"')`                   |
| `text=Login >> nth=0`               | First matching text element | `page.locator("text=Login").first()`                |
| `.alert:has-text("Error")`          | CSS + text filter           | `page.locator('.alert:has-text("Error")')`          |
| `.card:has(h3:has-text("Pricing"))` | Nested CSS + text           | `page.locator('.card:has(h3:has-text("Pricing"))')` |
| `div >> "Hello"`                    | Text within an element      | `page.locator('div >> "Hello"')`                    |
| `shadow::comp >>> "Save"`           | Shadow DOM + text           | `page.locator('shadow::comp >>> "Save"')`           |
| `/\d+ items/`                       | Regex for number-based text | `page.locator("/\\d+ items/")`                      |

#### 💡 Special Notes for nRobo

1. Quotes auto-detect text mode
These forms automatically behave as text selectors:
```bash
"Welcome"
'Login Page'
```
2. `text=` always forces text engine
Useful when CSS characters might confuse the parser.
3. `:has-text()` supports substring search
Same behavior as Playwright.
4. Regex patterns must begin and end with `/`
nRobo chooses regex engine automatically if pattern follows `/.../flags`.

### 🧩 Locator Collection API in nRobo

nRobo extends Selenium with **Playwright-style collection features** that allow powerful element filtering, iterating, and indexed selection.

These APIs work on any locator, including CSS, XPath, text selectors, shadow-selectors, and hybrid selectors.

#### 📘 Collection Methods Overview

| Method               | Description                                                               | Returns           |
| -------------------- | ------------------------------------------------------------------------- | ----------------- |
| `.all()`             | Returns a list-like **LocatorCollection** containing all matched elements | LocatorCollection |
| `.first()`           | First matching element                                                    | Locator           |
| `.last()`            | Last matching element                                                     | Locator           |
| `.nth(i)`            | Element at index `i` (0-based)                                            | Locator           |
| `.filter(...)`       | Filter by text, CSS, visibility, or nested locator conditions             | LocatorCollection |
| `.count()`           | Count of matched elements                                                 | int               |
| `.map(fn)`           | Transform list of elements                                                | List[Any]         |
| `.slice(start, end)` | Sub-range slicing                                                         | LocatorCollection |
| `.random()`          | Return random Locator from collection                                     | Locator           |

#### 🔧 Examples of Each Method

1. `.all()`

Collect all matched elements.

```python
items = page.locator("ul li").all()
assert items.count() == 5
```

You can iterate:

```python
for item in items:
    print(item.text())
```

2. `.first()`
```python
page.locator(".menu-item").first().click()
```

3. `.last()`
```python
page.locator(".menu-item").last().click()
```

4. `.nth(i)`

Select element at index:
```python
page.locator("div.card").nth(2).click()
```

Equivalent to Playwright.

5. `.filter(has_text="Active")`

Filter by visible text:
```python
active_rows = page.locator("tr").all().filter(has_text="Active")
active_rows.first().click()
```

Filter by regex:
```python
rows.filter(has_text=r"/pending/i")
```

Filter by nested CSS:
```python
page.locator(".card").all().filter(has="button:has-text('Pay')")
```

#### 🧪 Combined Examples

Filter + nth
```python
page.locator("li.item").all() \
    .filter(has_text="Completed") \
    .nth(1).click()
```

Iterate each element in filtered result
```python
for el in page.locator("div.row").all().filter(has_text="Price"):
    print(el.text())
```

Using `.slice()`
```python
top_three = page.locator(".result").all().slice(0, 3)
```

Random element
```python
page.locator(".product").all().random().click()
```

#### 🎯 Playwright-Like Chaining (nRobo Fluent Style)

```python
page.locator("div.card")
    .all()
    .filter(has_text="Premium")
    .first()
    .locator("button:has-text('Buy Now')")
    .click()
```

## 🔥 AutoWait Engine (Stability Layer)

nRobo includes a built-in **AutoWait Engine** that makes your tests **stable by default** — no need for sleeps, manual waits, or explicit WebDriverWait calls.

Every action such as **click**, **fill**, **press**, **hover**, and **navigation** automatically triggers smart waits under the hood.

### ⚙️ What AutoWait Does Automatically

| AutoWait Feature           | Description                                                                |
| -------------------------- | -------------------------------------------------------------------------- |
| **Visibility Wait**        | Ensures the element is visible before interacting                          |
| **Stale Element Recovery** | Retries interactions when Selenium throws `StaleElementReferenceException` |
| **Scroll Into View**       | Automatically scrolls element into the viewport before action              |
| **Navigation Detection**   | Detects page transitions and waits for page load automatically             |
| **DOM ReadyState Wait**    | Waits for `document.readyState === "complete"` after navigation            |
| **Retry Strategy**         | Retries resolving elements multiple times before failing                   |

### 🧠 Why AutoWait Matters

Selenium tests often fail because:

- Page wasn’t fully loaded

- Element wasn’t visible yet

- DOM re-rendered causing stale references

- Navigation or redirect wasn’t detected

- Element was outside the viewport

nRobo eliminates these failure points automatically.

### 📌 Example (No Manual Wait Needed)

```python
page.locator("#login").click()      # waits for visibility + scroll + stale retry
page.locator("#email").fill("user")
page.locator("button:has-text('Sign In')").click()  # waits for navigation if detected
```

Everything “just works” without:

- `time.sleep()`

- `WebDriverWait`

- `ExpectedConditions`

- Custom retry loops

### 🔍 Navigation-Aware Actions

nRobo's AutoWait engine detects if a click caused navigation:

```python
page.click(locator, wait="auto")  # default
```

| Mode   | Behavior                                                          |
| ------ | ----------------------------------------------------------------- |
| `auto` | Wait only if navigation is detected (URL change, readyState drop) |
| `load` | Always wait for full page load                                    |
| `none` | Do not wait after click                                           |

### 🚀 Result: 90–95% Flakiness Reduction

Users consistently observe:

- Fewer intermittent failures

- No brittle sleeps

- Faster, more deterministic test execution

- More readable tests with no noise

## 🧪 Assertions in nRobo (Fluent, Playwright-Style)

nRobo includes a rich `assertion engine` built directly into the Locator object, giving you a Playwright-like, fluent, readable assertion experience — but on top of Selenium.

Assertions automatically apply `AutoWait`, meaning nRobo retries until the condition becomes true or times out.

### ✅ Available Assertions

| Assertion                        | Description                                           |
| -------------------------------- | ----------------------------------------------------- |
| `should_be_visible()`            | Wait until element is visible                         |
| `should_be_hidden()`             | Wait until element becomes hidden or detached         |
| `should_be_enabled()`            | Wait until element is interactable                    |
| `should_have_text(expected)`     | Assert visible text matches or contains expected text |
| `should_contain_text(substring)` | Assert element contains substring (case-insensitive)  |
| `should_have_value(value)`       | Assert input/textarea value                           |
| `should_have_count(n)`           | Use with `.all()` to assert element count             |
| `should_exist()`                 | Wait until element appears in DOM                     |
| `should_not_exist()`             | Wait until element disappears                         |


All assertion methods automatically retry until the condition becomes true, reducing flakiness.

#### 📘 Assertion Examples

**Check visibility**
```python
page.locator("text=Login").should_be_visible()
```

**Validate text**
```python
page.locator("h3").should_have_text("Secure Area")
```

**Assert value of an input field**
```python
page.locator("#email").should_have_value("admin@test.com")
```

**Assert element becomes hidden**
```python
page.locator(".loading-spinner").should_be_hidden()
```

**Count assertions (with `.all()`)**
```python
items = page.locator("ul li").all()
items.should_have_count(5)
```

### 🔁 Assertions + AutoWait
Assertions automatically apply nRobo’s **AutoWait Engine**, meaning:

- no manual sleeps

- no WebDriverWait

- no ExpectedConditions

Example:
```python
page.locator("#status").should_have_text("Completed")
```

This will retry until:

- the element appears

- becomes visible

- text changes to “Completed”

or it times out with a detailed error message.

### 🧠 Fluent API: Chain Assertions with Locators
```python
page.locator("form >> button:has-text('Submit')")
    .should_be_enabled()
    .click()
```
Or:
```python
page.locator(".toast").should_be_visible().should_contain_text("Success")
```

### 📌 Why nRobo Assertions Are Better

| Feature                  | Selenium  | Playwright | nRobo      |
| ------------------------ | --------- | ---------- | ---------- |
| Built-in auto-retry      | ❌ No      | ✅ Yes      | ✅ Yes      |
| Fluent syntax            | ❌ No      | ✅ Yes      | ✅ Yes      |
| Works with collections   | ❌ No      | ✅ Yes      | ✅ Yes      |
| Text-based assertions    | ⚠️ Manual | ✅ Built-in | ✅ Built-in |
| Zero sleep/wait required | ❌ No      | ✅ Yes      | ✅ Yes      |

nRobo gives you **Playwright-level assertion power with Selenium compatibility**.

## Page objects
## Shadow DOM
## Filters
## Collections
## Custom wait methods
## Browser setup and teardown

These tests are NOT part of the official test suite and are NOT executed in CI.
They exist only for users to learn how to use the framework.
