from CommandLine import CommandLine
from typing import TYPE_CHECKING

if TYPE_CHECKING: # import for typechecking, but not at runtime
    from typing import Union, Any


CLI = CommandLine(atexit=exit, onerror=exit, prompt="> ", eofexit=True, interruptexit=True)

@CLI.command()
def hi(name="") -> None:
    """
    Print `Hi.` or `Hello {name}.` if supplied.

    Args:
        name (str, optional): The name of the object to say hi to. Defaults to "".

    Returns:
        None: returns None
    """

    return print(f"Hello {name}." if name else "Hi.") # print Hello name., or just Hi., then return None

if __name__ == "__main__":
    CLI().run()
