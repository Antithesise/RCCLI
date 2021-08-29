from typing import Union, Any


def check() -> None:
    try:
        err = False
        import termios # Only available on Unix terminals (like bash). Used to make stdin raw
    except ImportError:
        err = True
    
    if err:
        raise ModuleNotFoundError("Please run on a TTY-supporting (Unix) terminal.")
    else:
        del termios
