class ShadowSelectorParser:

    @staticmethod
    def parse(selector: str):
        """
        Returns a list of selector steps for shadow traversal.
        Example: "shadow::#a >>> .b >>> button"
        -> ["#a", ".b", "button"]
        """
        # remove "shadow::" prefixes
        selector = selector.replace("shadow::", "")

        # split traversal steps
        return [s.strip() for s in selector.split(">>>") if s.strip()]
