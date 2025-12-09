import re


class HasTextParser:
    @staticmethod
    def parse(selector: str):
        """
        Input: h3:has-text("abc")
        Output: ("h3", "abc")
        """
        pattern = r"^(.*?):has-text\((['\"])(.*?)\2\)$"
        match = re.match(pattern, selector.strip())

        if not match:
            raise ValueError(f"Invalid :has-text selector: {selector}")

        base_selector = match.group(1).strip()
        text_value = match.group(3).strip()

        return base_selector, text_value


class HasTextEngine:
    @staticmethod
    def to_xpath(base: str, text: str) -> str:
        return f'.//{base}[contains(normalize-space(.), "{text}")]'
