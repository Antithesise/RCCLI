from typing import TYPE_CHECKING

if TYPE_CHECKING: # import for typechecking, but not at runtime
    from typing import Union, Any


class Syntax:
    """
    A class for adding syntax highlighting to a piece of text.
    """

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

    def __unicode(self, text: str) -> str:
        """
        Escapes non-ASCII characters within text
        
        Args:
            text (str): The text to be cleaned.

        Returns:
            str: ASCII text
        """

        from fnmatch import fnmatch

        old = text

        if not "\\u001b" in text:
            try:
                text = self.unescape(str(bytes(text, "ascii").decode("unicode-escape")))
                self.outer.__index -= (len(old) - len(text))
            except (UnicodeDecodeError, DeprecationWarning, UnicodeEncodeError, UnicodeError, UnicodeWarning, UnicodeTranslateError, IndexError):
                text = old
        elif fnmatch(text, "*\\u001b[*"):
            text = text.replace("\\u001b[", "\u001b[")
            self.outer.__index -= (len(old) - len(text))

    def __multi_space(self, text: str) -> str:
        """
        Underline in red all areas with consecutive spaces.
        
        Args:
            text (str): The text to be cleaned.

        Returns:
            str: Underlined text
        """

        # underline in red all areas with more than 1 consecutive spaces
        txt = list(text)

        ins = 0

        for i, c in enumerate(txt):
            if c == " " and len(txt)-2 > i > 0:
                if txt[i-1+ins] == " " and txt[i-2+ins] != " ":
                    txt.insert(i, "\u001b[4m\u001b[31;1m")

                    ins += 1
                elif txt[i+1+ins] != " " and txt[i-1+ins] == " ":
                    txt.insert(i+2, "\u001b[0m")

                    ins += 1

        return "".join(txt)

    def __call__(self, text, underline=True, valid=False) -> Union[str, bool]:
        """
        Returns the callable that will be executed when the function is called .

        Args:
            text ([type]): The text to apply syntax highlighting to.
            underline (bool, optional): Whether to underline multiple spaces. Defaults to True.
            valid (bool, optional): Whether to check if the text contains any errors. Defaults to False.

        Returns:
            Union[str, bool]: The highlighted text, or whether the text is valid.
        """

        # define variable for modified text
        self.__stext = text
        # modify the text in that variable (order matters)
        if not valid:
            self.__unicode(self.__stext)
        if underline or valid:
            self.__multi_space(self.__stext)
        if valid:
            return "\\x1b[4m" not in repr(self.__stext) # return if text is valid
        return self.__stext # return the variable
