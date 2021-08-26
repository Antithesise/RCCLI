class Syntax:
    def __init__(self, outerinstance):
        self.outer = outerinstance
    
    def unescape(self, text: str) -> str:
        """
        Removes escaped Ansi escape sequences within a string.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: Ansi-less text
        """

        from re import compile

        return compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)

    def __unicode(self) -> None:
        """
        Escapes non-ASCII characters within self.__stext
        """

        from fnmatch import fnmatch

        old = self.__stext

        if not "\\u001b" in self.__stext:
            try:
                self.__stext = self.unescape(str(bytes(self.__stext, "ascii").decode("unicode-escape")))
                self.outer.__index -= (len(old) - len(self.__stext))
            except (UnicodeDecodeError, DeprecationWarning, UnicodeEncodeError, UnicodeError, UnicodeWarning, UnicodeTranslateError, IndexError):
                self.__stext = old
        elif fnmatch(self.__stext, "*\\u001b[*"):
            self.__stext = self.__stext.replace("\\u001b[", "\u001b[")
            self.outer.__index -= (len(old) - len(self.__stext))

    def __multi_space(self) -> None:
        """
        Underline in red all areas with consecutive spaces.
        """

        # underline in red all areas with more than 1 consecutive spaces
        self.__stext = self.__stext.replace("  ", "\u001b[4m\u001b[31;1m  \u001b[0m")
        self.__stext = self.__stext.replace("\u001b[4m\u001b[31;1m  \u001b[0m ", "\u001b[4m\u001b[31;1m   \u001b[0m")

    def __call__(self, text, underline=True, valid=False):
        # define variable for modified text
        self.__stext = text
        # modify the text in that variable (order matters)
        if not valid:
            self.__unicode()
        if underline or valid:
            self.__multi_space()
        if valid:
            return "\\x1b[4m" not in repr(self.__stext) # return if text is valid
        return self.__stext # return the variable
