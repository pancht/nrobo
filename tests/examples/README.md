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

page.selector("text=Login").click()

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
items = page.selector("ul li").all()
assert items.count() == 5
```

You can iterate:

```python
for item in items:
    print(item.text())
```

2. `.first()`

```python
page.selector(".menu-item").first().click()
```

3. `.last()`

```python
page.selector(".menu-item").last().click()
```

4. `.nth(i)`

Select element at index:

```python
page.selector("div.card").nth(2).click()
```

Equivalent to Playwright.

5. `.filter(has_text="Active")`

Filter by visible text:

```python
active_rows = page.selector("tr").all().filter(has_text="Active")
active_rows.first().click()
```

Filter by regex:
```python
rows.filter(has_text=r"/pending/i")
```

Filter by nested CSS:

```python
page.selector(".card").all().filter(has="button:has-text('Pay')")
```

#### 🧪 Combined Examples

Filter + nth

```python
page.selector("li.item").all()
    .filter(has_text="Completed")
    .nth(1).click()
```

Iterate each element in filtered result

```python
for el in page.selector("div.row").all().filter(has_text="Price"):
    print(el.text())
```

Using `.slice()`

```python
top_three = page.selector(".result").all().slice(0, 3)
```

Random element

```python
page.selector(".product").all().random().click()
```

#### 🎯 Playwright-Like Chaining (nRobo Fluent Style)

```python
page.selector("div.card")
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
page.selector("#login").click()  # waits for visibility + scroll + stale retry
page.selector("#email").fill("user")
page.selector("button:has-text('Sign In')").click()  # waits for navigation if detected
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
page.selector("text=Login").should_be_visible()
```

**Validate text**

```python
page.selector("h3").should_have_text("Secure Area")
```

**Assert value of an input field**

```python
page.selector("#email").should_have_value("admin@test.com")
```

**Assert element becomes hidden**

```python
page.selector(".loading-spinner").should_be_hidden()
```

**Count assertions (with `.all()`)**

```python
items = page.selector("ul li").all()
items.should_have_count(5)
```

### 🔁 Assertions + AutoWait
Assertions automatically apply nRobo’s **AutoWait Engine**, meaning:

- no manual sleeps

- no WebDriverWait

- no ExpectedConditions

Example:

```python
page.selector("#status").should_have_text("Completed")
```

This will retry until:

- the element appears

- becomes visible

- text changes to “Completed”

or it times out with a detailed error message.

### 🧠 Fluent API: Chain Assertions with Locators

```python
page.selector("form >> button:has-text('Submit')")
.should_be_enabled()
.click()
```
Or:

```python
page.selector(".toast").should_be_visible().should_contain_text("Success")
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

## 🧩 Page Objects
The **Page Object Model (POM)** in nRobo organizes your UI automation code into reusable, readable, and maintainable components.

Each **Page Object** represents a specific page or screen of your application.
It encapsulates both the locators (selectors used to find elements) and the actions (methods that operate on those elements) in a single class.

📂 Directory Structure
```python
pages/
 ├─ login_page.py
 ├─ login_page_locators.py
 ├─ dashboard_page.py
 └─ dashboard_page_locators.py
```

Each page has two files:

- `<page_name>.py` — defines the Page Object class extending `BasePage`

- `<page_name>_locators.py` — defines a corresponding `Locators` class

### 🧱 Example: Login Page

**File:** `pages/login_page.py`

```python
from nrobo.pages.base_page import BasePage
from pages.login_page_locators import LoginPageLocators

class LoginPage(BasePage):
    """Page Object for Login Page."""

    loc = LoginPageLocators()

    def open_page(self):
        return self.open("https://example.com/login")

    def login(self, username, password):
        self.locator(self.loc.USERNAME).fill(username)
        self.locator(self.loc.PASSWORD).fill(password)
        self.locator(self.loc.LOGIN_BTN).click()
        return self
```

**File:** `pages/login_page_locators.py`

```python
"""Locators for Login Page."""

class LoginPageLocators:
    USERNAME = "#username"
    PASSWORD = "#password"
    LOGIN_BTN = "button:has-text('Login')"
```

### ⚙️ Generating Page Objects Automatically

You can auto-generate a new Page Object and its locator file using:

```bash
nrobo generate page <PageName>
```

Example:
```bash
nrobo generate page LoginPage
```

**Creates:**

```bash
✔ Created page: pages/login_page.py
✔ Created locator file: pages/login_page_locators.py
```

### 💡 Best Practices

- Keep selectors centralized in locator files.

- Add clear docstrings and method names for all actions.

- Follow consistent naming: `LoginPage`, `DashboardPage`, `SettingsPage`, etc.

- Use methods like `.open()`, `.click()`, `.fill()`, and `.should_have_text()` from `BasePage` or `SeleniumWrapper`.

## 🔍 Filters

**Filters** in nRobo provide a concise and chainable way to refine element collections and perform targeted assertions on groups of DOM elements.
They enable expressive querying and bulk operations while maintaining readable, declarative test code.

### 💡 Concept

When a locator matches **multiple elements**, a filter allows you to:

- Narrow down the matched set (by index, text, or attribute)

- Retrieve specific elements (`first()`, `last()`, `nth(n)`)

- Chain actions or assertions on the filtered element(s)

Filters are available on any `Locator` instance returned from:

```python
page.selector("selector")
```

### ⚙️ Common Filter Methods
| Method                       | Description                                          | Example                                                   |
| :--------------------------- | :--------------------------------------------------- | :-------------------------------------------------------- |
| `.all()`                     | Returns all matched elements as a list               | `page.locator(".card").all()`                             |
| `.first()`                   | Selects the first matching element                   | `page.locator(".item").first().click()`                   |
| `.last()`                    | Selects the last matching element                    | `page.locator(".item").last().should_have_text("Logout")` |
| `.nth(index)`                | Selects the element at the specified index (0-based) | `page.locator(".row").nth(2).click()`                     |
| `.filter(text="...")`        | Filters elements containing the given text           | `page.locator("button").filter(text="Submit").click()`    |
| `.filter(attribute="value")` | Filters elements by attribute value                  | `page.locator("input").filter(placeholder="Email")`       |

### 🧱 Example Usage

```python
def test_filter_usage(page):
    page.goto("https://example.com")

    # Select first card
    page.selector(".card").first().should_be_visible()

    # Select last product name
    page.selector(".product-name").last().should_have_text("Deluxe Edition")

    # Select third button
    page.selector("button").nth(2).click()

    # Filter by text content
    page.selector("button").filter(text="Login").click()

    # Filter by attribute
    page.selector("input").filter(placeholder="Search").fill("nRobo")
```

### 🧠 Notes & Best Practices

- Always prefer `semantic selectors` (data-test-id, aria-label, etc.) over nth-based selection.

- Use filters when multiple identical elements exist and you want to clarify intent.

- Filters can be chained with assertions:

```python
page.selector(".menu-item").filter(text="Settings").should_be_visible()
```

- Combine `.all()` with loops for batch assertions:

```python
for item in page.selector(".product").all():
    item.should_be_visible()
```

### 🧩 Integration Example with Locators

You can define reusable locators that leverage filter patterns:
```python
class DashboardLocators:
    MENU_ITEMS = ".menu-item"
    ACTIVE_MENU_ITEM = ".menu-item.active"
```
```python
class DashboardPage(BasePage):
    loc = DashboardLocators()

    def open_menu(self, name):
        self.locator(self.loc.MENU_ITEMS).filter(text=name).click()
```

### ⚖️ Filter vs Locator — Comparison

| Aspect                          | **Locator**                                                                 | **Filter**                                                                     |
| :------------------------------ | :-------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| **Purpose**                     | Finds elements on the page using a selector.                                | Narrows down results from an existing locator’s element set.                   |
| **Scope**                       | Operates at the **DOM query** level — retrieves all matches for a selector. | Operates at the **collection** level — refines already-found elements.         |
| **Typical Use Case**            | Identify a base set of elements or single unique target.                    | Target a specific element among multiple similar ones.                         |
| **Definition Style**            | Usually defined in `*_locators.py` classes as constants.                    | Used directly in Page Object methods or test logic for fine-grained selection. |
| **Return Type**                 | A `Locator` object that can represent one or more elements.                 | A new filtered `Locator` (or list via `.all()`) from the parent locator.       |
| **Example – Base Selection**    | `page.locator("#username")`                                                 | —                                                                              |
| **Example – Refined Selection** | —                                                                           | `page.locator(".button").filter(text="Login")`                                 |
| **Example – Index Access**      | —                                                                           | `page.locator(".row").nth(1)`                                                  |
| **Example – Chaining**          | `page.locator(".menu-item").click()`                                        | `page.locator(".menu-item").filter(text="Settings").click()`                   |
| **Performance**                 | Triggers a fresh DOM query each time.                                       | Works on cached element handles within the parent locator’s context.           |
| **Best For**                    | Stable, reusable element definitions (single source of truth).              | Contextual or dynamic content selection at runtime.                            |
| **Usage Location**              | Locators are stored in `Locators` classes for maintainability.              | Filters are invoked inline inside Page methods or test steps.                  |
| **Example in nRobo Project**    | `LoginPageLocators.LOGIN_BTN = "button:has-text('Login')"`                  | `page.locator(LoginPageLocators.LOGIN_BTN).filter(text="Login")`               |

### 🧭 Guidelines

- **Define once, filter many**.
Keep locators centralized, but apply filters where context demands specificity.

- **Avoid over-filtering**.
If you routinely use the same filter, consider defining a dedicated locator instead.

- **Chain responsibly**.
Filters can be combined (.filter(...).first()) but should stay readable.

## 📚 Collections

**Collections** in nRobo represent **groups of elements** located by a shared selector or locator.
They provide an intuitive way to perform **batch operations**, **aggregated assertions**, or **loop-based verifications** over multiple UI elements returned by a locator query.

A `Collection` is essentially an iterable abstraction built on top of `Locator` results — giving you the power to work with multiple elements in a clean, expressive, and consistent way.

### 💡 Concept

When a locator matches **multiple elements**, nRobo wraps them into a **Collection** object.
This allows you to:

- Access each element individually (`.first()`, `.last()`, `.nth(i)`)

- Iterate through all elements using `.all()` or a loop

- Apply bulk checks and assertions in a readable style

- Keep your test code declarative and framework-consistent

### ⚙️ Common Collection Methods

| Method              | Description                                               | Example                                                                                   |
| :------------------ | :-------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| `.all()`            | Returns all elements as a list of Locators                | `cards = page.locator(".card").all()`                                                     |
| `.count()`          | Returns the number of matched elements                    | `count = page.locator(".card").count()`                                                   |
| `.first()`          | Returns the first element in the collection               | `page.locator(".row").first().click()`                                                    |
| `.last()`           | Returns the last element in the collection                | `page.locator(".row").last().should_have_text("Summary")`                                 |
| `.nth(index)`       | Returns the element at the given index (0-based)          | `page.locator(".product").nth(1).click()`                                                 |
| `.filter(**kwargs)` | Refines elements based on text, attributes, or conditions | `page.locator(".item").filter(text="Buy Now")`                                            |
| `.map(func)`        | Applies a function or action to each element              | `page.locator(".checkbox").map(lambda el: el.click())` *(if supported in implementation)* |

### 🧱 Example Usage

```python
def test_product_cards(page):
    page.goto("https://example.com/products")

    cards = page.selector(".product-card")

    # Verify total number of products
    assert cards.count() == 5

    # Loop over all product cards
    for card in cards.all():
        card.should_be_visible()

    # Click on the second product
    cards.nth(1).click()

    # Assert last product name
    cards.last().should_have_text("Deluxe Edition")
```

🧩 Combined Example: Locator + Collection + Filter

```python
def test_select_specific_button(page):
    buttons = page.selector("button")

    # Total buttons
    assert buttons.count() >= 3

    # Filter the collection by text
    buttons.filter(text="Submit").first().click()

    # Loop through all visible buttons
    for btn in buttons.all():
        btn.should_be_visible()
```

### 🧠 Best Practices

- Treat a Collection as a **readable**, **iterable set** of elements — not just a list.

- Always use `.count()` or `.all()` before asserting the expected number of elements.

- Prefer `.filter()` + `.first()` over hard-coded indexes for stability.

- Avoid deeply nested loops; instead, encapsulate repetitive logic into Page methods.


### 🔗 Related Concepts

| Related Concept | Description                                                    |
| :-------------- | :------------------------------------------------------------- |
| **Locator**     | Defines how elements are identified in the DOM.                |
| **Filter**      | Narrows down matched elements within a collection.             |
| **Page Object** | Encapsulates locators and actions for a complete page or view. |


## ⏳ Custom Wait Methods

**Custom Wait Methods** in `nRobo` provide a powerful and expressive way to handle dynamic page synchronization.
They abstract the complexity of explicit waits and make your tests **resilient**, **readable**, and **deterministic** across varying network or render conditions.

Unlike generic Selenium or Playwright waits, `nRobo`’s custom wait methods are **built around intelligent polling and auto-timeouts** defined in framework settings — giving every test the right balance between speed and reliability.

### 💡 Purpose

Dynamic web pages often require waiting for elements to appear, disappear, or reach a specific state before performing an action.
`nRobo` provides high-level custom wait utilities so you can focus on intent, not timing logic.


### ⚙️ Common Wait Methods

| Method                                                   | Description                                                           | Example                                                      |
| :------------------------------------------------------- | :-------------------------------------------------------------------- | :----------------------------------------------------------- |
| `wait_for_visible(locator, timeout=None)`                | Waits until the element is visible on the page.                       | `page.wait_for_visible("#login")`                            |
| `wait_for_clickable(locator, timeout=None)`              | Waits until the element becomes visible and enabled for interaction.  | `page.wait_for_clickable(".submit-btn")`                     |
| `wait_for_disappear(locator, timeout=None)`              | Waits until the element is no longer visible or removed from the DOM. | `page.wait_for_disappear(".loading-spinner")`                |
| `wait_for_text(locator, text, timeout=None)`             | Waits until the given text appears in the element.                    | `page.wait_for_text(".message", "Success")`                  |
| `wait_until(condition_fn, timeout=None, interval=0.5)`   | Waits for a custom condition (lambda or function) to return True.     | `page.wait_until(lambda: "Ready" in page.get_status_text())` |
| `wait_for_attribute(locator, attr, value, timeout=None)` | Waits until an attribute’s value matches expectation.                 | `page.wait_for_attribute(".status", "data-state", "loaded")` |


### 🧱 Example Usage

```python
def test_login_flow(page):
    page.goto("https://example.com/login")

    page.wait_for_visible("#username")
    page.selector("#username").fill("nrobo_user")
    page.selector("#password").fill("secret123")

    page.wait_for_clickable("button:has-text('Login')")
    page.selector("button:has-text('Login')").click()

    # Wait until dashboard appears
    page.wait_for_visible("#dashboard")
    page.wait_for_text("#welcome", "Welcome back")
```

### 🧩 Advanced Usage — Custom Condition

```python
def test_dynamic_refresh(page):
    page.goto("https://example.com/data")

    # Wait for custom condition
    page.wait_until(
        lambda: "Updated" in page.selector("#status").text(),
        timeout=10,
        interval=0.25
    )

    page.selector("#status").should_have_text("Updated Successfully")
```

### ⚙️ AutoWait vs Custom Wait

| Aspect           | **AutoWait (Implicit)**                                                   | **Custom Wait (Explicit)**                               |
| :--------------- | :------------------------------------------------------------------------ | :------------------------------------------------------- |
| **Triggered by** | Built-in automatic waiting in locator actions (`click()`, `fill()`, etc.) | Manually called by test code when dynamic sync is needed |
| **Usage**        | Implicitly happens under the hood                                         | Explicit call: `wait_for_visible()`                      |
| **Control**      | Framework decides when to pause                                           | Tester defines logic and timeout                         |
| **Best for**     | Stable UI interactions                                                    | Conditional, delayed, or dynamic elements                |
| **Example**      | `page.locator("#submit").click()`                                         | `page.wait_for_disappear(".loading")`                    |


### 🧠 Best Practices

- Always use **custom waits** for **dynamic content** or **asynchronous loading**.

- Prefer semantic waits (e.g., “wait for success message”) instead of arbitrary sleeps.

- Centralize timeout settings in framework config (`settings.DEFAULT_WAIT_TIMEOUT`).

- Combine waits with assertions for robust test reliability.

- Avoid `time.sleep()` — use `wait_for_*` methods to stay deterministic.

### 🔗 Related Features

| Feature        | Description                                                         |
| :------------- | :------------------------------------------------------------------ |
| **AutoWait**   | Built-in element synchronization handled by nRobo’s locator engine. |
| **Assertions** | Can implicitly use waits (`should_have_text`, `should_be_visible`). |
| **Settings**   | Configure default wait timeout and polling intervals globally.      |


## 🌐 Browser Setup and Teardown

Browser setup and teardown in `nRobo` are fully automated and designed to ensure each test runs in a **clean**, **isolated environment**.
The framework abstracts driver management, session initialization, and cleanup through unified wrappers and Pytest fixtures — minimizing boilerplate while maximizing reliability.

### 💡 Purpose

Every UI test depends on a browser session.
`nRobo` ensures consistent browser lifecycle management by automatically handling:

- Launching the browser before test execution

- Initializing driver/session with chosen options

- Managing cookies, storage, and window state

- Gracefully quitting after the test run or on failure

- This approach prevents **session leakage**, ensures **test independence**, and makes local and CI executions **environment-agnostic**.


### ⚙️ Default Browser Setup

By default, `nRobo` launches the browser based on CLI or configuration settings.

Example CLI usage:
```bash
nrobo --browser chrome
```

Under the hood:
```python
@pytest.fixture(scope="function")
def page(get_driver):
    """Fixture that provides a wrapped Selenium or Playwright page object."""
    driver = get_driver(browser_name="chrome", headless=False)
    yield driver
    driver.quit()
```

The `get_driver()` utility dynamically returns the driver object configured via framework settings (`nrobo.core.settings`) or CLI flags.

### 🧱 Example Setup Flow

1. Configuration Detection
Framework reads browser and headless mode from CLI or environment variables.
```bash
nrobo run --browser edge --headless
```

2. Driver Initialization
Driver instance created via `get_driver()`:
```python
driver = get_driver(browser_name="edge", headless=True)
```

3. Session Wrapper Binding
The driver is wrapped in `SeleniumWrapper` or `PlaywrightWrapper` for higher-level APIs:
```python
page = SeleniumWrapper(driver)
```

4. Test Execution
Each test runs using the `page`  fixture, which automatically manages wait conditions, assertions, and cleanup hooks.

5. Teardown (Automatic)
After the test completes (pass or fail), the browser session is closed:
```python
driver.quit()
```

### 🧩 Custom Setup Example

You can override setup or extend preconditions at the test or suite level:

```python
@pytest.fixture(scope="function")
def login_page(get_driver):
    page = get_driver(browser_name="chrome")
    page.goto("https://example.com/login")
    page.selector("#username").fill("demo_user")
    page.selector("#password").fill("demo_pass")
    page.selector("button:has-text('Login')").click()
    yield page
    page.quit()
```



### 🧹 Custom Teardown Logic

You can add teardown logic such as log collection, screenshot capture, or session clearing:
```python
def teardown_function(request, page):
    if request.node.rep_call.failed:
        page.take_screenshot("failed_test.png")
    page.quit()
```

Or integrate it via Pytest hooks:
```python
def pytest_runtest_teardown(item):
    # Custom teardown hook
    pass
```

### ⚙️ Supported Browsers

| Browser               | Driver Managed By                                         | CLI Example                   |
| :-------------------- | :-------------------------------------------------------- | :---------------------------- |
| **Chrome / Chromium** | `webdriver_manager.chrome.ChromeDriverManager()`          | `nrobo run --browser chrome`  |
| **Firefox**           | `webdriver_manager.firefox.GeckoDriverManager()`          | `nrobo run --browser firefox` |
| **Edge**              | `webdriver_manager.microsoft.EdgeChromiumDriverManager()` | `nrobo run --browser edge`    |
| **Safari**            | Native WebDriver (macOS only)                             | `nrobo run --browser safari`  |


Playwright-based sessions can also be configured if your project uses Playwright bindings.

### 🧠 Best Practices

- Always use framework fixtures (page, get_driver) instead of manually instantiating WebDrivers.

- Use **function-level scope** for isolation; use **session-level** only for controlled setups (e.g., global logins).

- Prefer headless=True in CI environments for performance.

- Integrate teardown hooks for screenshots, logs, and Allure attachments.

- Never reuse driver instances between tests unless explicitly scoped.

### 🔗 Related Topics

| Feature                                 | Description                                                                 |
| :-------------------------------------- | :-------------------------------------------------------------------------- |
| **SeleniumWrapper / PlaywrightWrapper** | Provides uniform APIs for browser actions and assertions.                   |
| **Fixtures**                            | Supplies browser/session objects to tests automatically.                    |
| **CLI Options**                         | Control browser type, headless mode, and suite execution.                   |
| **Allure Reporting**                    | Integrates screenshots and environment info captured during setup/teardown. |


These tests are NOT part of the official test suite and are NOT executed in CI.
They exist only for users to learn how to use the framework.
