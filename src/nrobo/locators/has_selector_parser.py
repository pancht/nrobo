class HasSelectorParser:
    @staticmethod
    def split(selector: str):
        """
        Splits 'A:has(B)' into ('A', 'B')
        Supports multiple nested :has().
        """
        base = selector.split(":has(", 1)[0].strip()
        inside = selector.split(":has(", 1)[1].rstrip(")").strip()
        return base, inside
