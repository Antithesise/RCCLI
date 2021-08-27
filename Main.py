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
def help(command="") -> None:
    """Print help for a given command.

    Args:
        command (str, optional): [description]. Defaults to "".

    Raises:
        KeyError: [description]

    Returns:
        NoneType: returns None
    """

    settings = CLI.config

    if command in CLI.commands.keys(): # CLI.commands is a dict of commands names and functions
        n = command
        f = CLI.commands[command]

        fdocs = ""
        fargs = []

        if f.doc:
            fdocs = "\n\t".join(f.doc.strip().split("\n")) # reformat the function's doc strings

        for attr in f.__code__.co_varnames: # for each local variable in the function
            if attr[0] != "" and attr != "settings": # if it is not named settings or starts with a ''
                fargs += [attr] # add it to the list of variables

        fargs = ", ".join(fargs) # then format that list

        return print(f"\r{n}({fargs}):\n\n\r\t{fdocs}\n") # print it all out nicely and returns None
    
    elif command != "":
        if settings["onerror"] == exit:
            raise KeyError("Command not found.") # raise an error if the settings say that is allowed
        else:
            return settings["onerror"]() # otherwise return the ouput of on error func

    for n, f in CLI.commands.items():
        fdocs = ""
        fargs = []

        if f.doc:
            fdocs = "\n\t".join(f.doc.strip().split("\n"))

        for attr in f.__code__.co_varnames:
            if attr[0] != "" and attr != "settings":
                fargs += [attr]

        fargs = ", ".join(fargs)

        print(f"\r{n}({fargs}):\n\n\r\t{fdocs}\n")

@CLI.command()
def hi(name="") -> None:
    """
    Print `Hi.` or `Hello {name}.` if supplied.

    Args:
        name (str, optional): The name of the object to say hi to. Defaults to "".

    Returns:
        NoneType: returns None
    """

    return print(f"Hello {name}." if name else "Hi.") # print Hello name., or just Hi., then return None

CLI().run()
