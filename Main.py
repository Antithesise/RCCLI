from CommandLine import CommandLine
from typing import TYPE_CHECKING

if TYPE_CHECKING: # import for typechecking, but not at runtime
    from typing import Any

CLI = CommandLine(atexit=exit, onerror=exit, prompt="> ", eofexit=True, interruptexit=True)

@CLI.command()
def exit(status="0") -> 'Any':
    """Exit with a given status code.

    Args:
        status (str, optional): The status to exit with. Prints status if NaN and status will = 0 (I.e., a failure). Defaults to "0".

    Returns:
        Any: [description]
    """

    from sys import exit as exit

    settings = CLI.config

    if status == "0":
        return settings["atexit"]()
    elif status.isdigit():
        exit(int(status))

    return print(status) or status

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
