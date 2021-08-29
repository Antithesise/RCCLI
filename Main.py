from CommandLine import CommandLine
from typing import Union, Any

if __name__ == "__main__":
    CLI = CommandLine(atexit=exit, onerror=exit, prompt="> ", eofexit=True, interruptexit=True)
else:
    class CLI:
        def command():
            def decorator_command(func: function):
                from functools import wraps
                
                @wraps(func)
                def wrapper_command(*args, **kwargs):

                    return func(*args, **kwargs)

                return wrapper_command

            return decorator_command

@CLI.command()
def hi(name="") -> None:
    """
    Print `Hi.` or `Hello {name}.` if supplied.

    Args:
        name (str, optional): The name of the object to say hi to. Defaults to "".

    Returns:
        None: returns None.
    """

    return print(f"Hello {name}." if name else "Hi.") # print Hello name., or just Hi., then return None

if __name__ == "__main__":
    CLI().run()
