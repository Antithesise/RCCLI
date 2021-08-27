def getpass(prompt) -> str:
    """
    This function gets input from the user without echoing their characters. Unlike the stdlib module, this functions echos '•' instead of the user's keystrokes.

    Args:
        prompt (str): The string to prompt the user with.

    Raises:
        ModuleNotFOundError: When running on a terminal without TTY-support.

    Returns:
        str: The password entered by the user.
    """

    from sys import stdin, stdout
    from tty import setraw

    err = False

    try:
        from termios import tcgetattr,  tcsetattr, TCSADRAIN # Only available on Unix terminals (like bash). Used to make stdin raw
    except ImportError:
        err = True
    
    if err:
        raise ModuleNotFoundError("Please run on a TTY-supporting (Unix) terminal.")

    __old_settings = tcgetattr(stdin) # store old tty settings

    uinput = ""
    __index = 0

    print(end=prompt)

    while True:
        setraw(stdin) # stop tty from accessing stdin

        char = ord(stdin.read(1))

        if char in [3, 5, 10, 13]: # enter
            tcsetattr(stdin.fileno, TCSADRAIN, __old_settings)

            return uinput
        elif char == 27: # arrow keys
            next1, next2 = ord(stdin.read(1)), ord(stdin.read(1))

            if next1 == 91:
                if next2 == 68: # Left
                    __index = max(0, __index - 1)
                elif next2 == 67: # Right
                    __index = min(len(uinput), __index + 1)
        elif char in range(32, 127):
            uinput = uinput[:__index] + chr(char) + uinput[__index:]

            __index += 1
        elif char == 127: # delete
            uinput = uinput[:__index - 1] + uinput[__index:]

            __index -= 1

        stdout.write(f"\r\u001b[0K{('•' * len(uinput))}\r" + (f"\u001b[{__index}C" if __index > 0 else ""))
        stdout.flush()

        tcsetattr(stdin.fileno, TCSADRAIN, __old_settings)
        