class PseudoSelectorParser:

    @staticmethod
    def split(selector: str):
        """
        Splits into (base_selector, pseudo_list)
        Example:
            "button:visible" -> ("button", [":visible"])
        """
        parts = selector.split(":")
        base = parts[0].strip() if parts[0].strip() else "*"

        pseudos = []
        for part in parts[1:]:
            if part.startswith("not("):
                pseudos.append(f":not({part[4:].rstrip(')')})")
            else:
                pseudos.append(":" + part.strip())

        return base, pseudos
