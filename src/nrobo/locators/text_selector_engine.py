class TextSelectorEngine:

    @staticmethod
    def find_by_text(driver, text: str):
        """
        Return elements whose visible text matches text exactly or partially.
        """
        script = """
        const text = arguments[0].toLowerCase();
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);

        const matches = [];
        while(walker.nextNode()) {
            const el = walker.currentNode;
            const visible = !!( el.offsetWidth || el.offsetHeight || el.getClientRects().length );
            if (!visible) continue;

            const t = (el.innerText || "").toLowerCase();
            if (t.includes(text)) {
                matches.push(el);
            }
        }
        return matches;
        """
        return driver.execute_script(script, text.strip())

    @staticmethod
    def regex_match(driver, pattern: str):
        script = """
        const regex = new RegExp(arguments[0], 'i');
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
        const out = [];

        while(walker.nextNode()) {
            const el = walker.currentNode;
            const visible = !!( el.offsetWidth || el.offsetHeight || el.getClientRects().length );
            if (!visible) continue;

            if (regex.test(el.innerText || "")) {
                out.push(el);
            }
        }
        return out;
        """
        return driver.execute_script(script, pattern)

    @staticmethod
    def find_has_text(driver, css_selector: str, text: str):
        """
        Example: 'button:has-text("Save")'
        Must return buttons whose descendant text matches.
        """
        script = """
        const selector = arguments[0];
        const text = arguments[1].toLowerCase();
        const nodes = document.querySelectorAll(selector);
        const matches = [];

        nodes.forEach(el => {
            const t = (el.innerText || "").toLowerCase();
            if (t.includes(text)) {
                matches.push(el);
            }
        });

        return matches;
        """
        return driver.execute_script(script, css_selector, text)
