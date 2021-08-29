from typing import Union, Any


class CommandLine:
    """
    Python based utility for creating CLIs and other commandline-driven utilities.
    """

    def __init__(self, **config):
        """
        Python based utility for creating CLIs and other commandline-driven utilities.

        Args:
            atexit (object, optional): The object to be called at the exiting of the program. Defaults to `exit`.
            onerror (object, optional): The object to be called in the event of a program error. Defaults to `exit`.
            prompt (str, optional): The str to prompt the user for input. Defaults to "> ".
            eofexit (bool, optional): Whether to exit on EOF (Ctrl+D).
            interruptexit (bool, optional): Whether to exit on Keyboard Interrupt (Ctrl+C).
            password (Union[str, None], optional): The password for the application. Defaults tp `None`.

        Raises:
            ModuleNotFOundError: When running on a terminal without TTY-support.

        Returns:
            CommandLine: An instance of the CommandLine class.
        """

        from CommandLine.ext.CheckUnix import check

        check()

        self.config = {k.lower():v for k, v in config.items()} # self.config = config, but all keys are loweraces

        defaults = { # default configuration settings
            "atexit": exit,
            "onerror": exit,
            "prompt": "> ",
            "eofexit": True,
            "interruptexit": True,
            "password": None
        }

        for k in defaults.keys(): # for each configuration setting
            if k not in self.config: # if user hasn't specified that specific setting
                self.config[k] = defaults[k] # set that setting to the default
                
                if k == "onerror" and k not in defaults: # if atexit is set and onerror isn't
                    self.config[k] = self.config["atexit"] # set onerror to atexit

                self.__setattr__(k, self.config[k])
        
        self.commands = {}

    def reset(self) -> None:
        """
        Reset the terminal settings to the default settings.

        Returns:
            None: returns None.
        """

        from termios import tcsetattr, TCSADRAIN
        from sys import stdin

        return tcsetattr(stdin.fileno, TCSADRAIN, self.__old_settings)

    def command(self, auth: bool=False) -> 'Union[Any, None]':
        """
        Decorator that adds a function as a command.

        Args:
            auth (bool, optional): Whether authentication is needed to perform the function. Ignored if password is not specified. Defaults to `False`.

        Returns:
            Union[Any, None]: returns the output of the function or None if execution is cancelled.
        """

        def decorator_command(func):
            from functools import wraps

            settings = self.config

            self.commands[func.__name__] = func

            @wraps(func)
            def wrapper_command(*args, **kwargs):
                if self.auth != settings["password"] != None and auth:
                    if self.authu() == False:
                        return print("Command exited before execution")

                return func(*args, **kwargs)
            return wrapper_command
        return decorator_command

    def help(self, command="") -> None:
        """
        Print help for a given command.

        Args:
            command (str, optional): the name of the command to get help on. Defaults to "".

        Raises:
            KeyError: If command does not match any registered command.

        Returns:
            None: returns None.
        """

        settings = self.config

        if command in self.commands.keys(): # self.commands is a dict of commands names and functions
            n = command
            f = self.commands[command]

            fdocs = ""
            fargs = []

            if f.doc:
                fdocs = "\n\t".join(f.doc.strip().split("\n")) # reformat the function's doc strings

            for attr in f.__code__.co_varnames: # for each local variable in the function
                if attr[0] != "_" and attr != "settings": # if it is not named settings or starts with a '_'
                    fargs += [attr] # add it to the list of variables

            fargs = ", ".join(fargs) # then format that list

            return print(f"\r{n}({fargs}):\n\n\r\t{fdocs}\n") # print it all out nicely and returns None
        
        elif command != "":
            if settings["onerror"] == exit:
                raise KeyError("Command not found.") # raise an error if the settings say that is allowed
            else:
                return settings["onerror"]() # otherwise return the ouput of on error func

        for n, f in self.commands.items():
            fdocs = ""
            fargs = []

            if f.doc:
                fdocs = "\n\t".join(f.doc.strip().split("\n"))

            for attr in f.__code__.co_varnames:
                if attr[0] != "" and attr != "settings":
                    fargs += [attr]

            fargs = ", ".join(fargs)

            print(f"\r{n}({fargs}):\n\n\r\t{fdocs}\n")

    def exit(self, status: str="0") -> 'Union[str, Any]':
        """
        Exit with a given status code.

        Args:
            status (str, optional): The status to exit with. Prints status if NaN and status will = 0 (I.e., a failure). Defaults to "0".

        Returns:
            Union[str, Any]: status, or the output of ATEXIT.
        """

        from sys import exit as _exit

        settings = self.config

        if status == "0":
            return settings["atexit"]()
        elif status.isdigit():
            _exit(int(status))

        return print(status) or status # returns status as print outputs None

    def execute(self, name: str, *args, **kwargs) -> 'Union[Any, None]':
        """
        Execute a command.

        Args:
            name (str): the name of the command to be called.
            args (any): arguments to be supplied to the command.
            kwargs (any): named arguments to be supplied to the command.

        Raises:
            KeyError: If the command is not found.
            TypeError: Incorrect number of arguments given.

        Returns:
            Union[Any, None]: return the output of the command, None if execution is cancelled or ONERROR.
        """

        settings = self.config

        if name not in self.commands: # if name is not a valid command
            if settings["onerror"] == exit:
                raise KeyError("Command not found.") # raise an error if the settings say that is allowed
            else:
                return settings["onerror"]() # otherwise return the ouput of on error func
        
        try:
            return self.commands[name](*args, **kwargs) # return the output of the command
        except TypeError:
            if settings["onerror"] == exit:
                raise TypeError("Incorrect number of arguments given.")
            else:
                return settings["onerror"]()

    def run(self, auth=None) -> 'Any':
        """
        Runs the commandline utility created by the user.

        Args:
            auth (Union[None, str], optional): The auth password (if any) to authorise the utility at runtime.

        Returns:
            Any: Returns the output of either ONERROR or ATEXIT.
        """


        settings = self.config

        self.auth = auth

        if self.auth != None:
            if settings["onerror"] == exit:
                assert settings["password"] != None # raise an error if the settings say that is allowed
            else:
                return settings["onerror"]() # otherwise return the ouput of on error func
        
        return self()

    def authu(self) -> None:
        """
        Get the user to authorise themselves.

        Returns:
            Union[None, bool]: None, or False if user cancelled.
        """


        from CommandLine.ext import getpass

        settings = self.config

        if settings["password"] != None:
            while self.auth != settings["password"]:
                self.auth = getpass("Password: ")
                if self.auth == settings["password"]:
                    break
                elif self.auth in [chr(3),chr(5)]:
                    return False
                print("Incorrect!")
        

    def __call__(self) -> 'Any':
        """
        Runs the commandline utility created by the user.

        Returns:
            Any: Returns the output of either ONERROR or ATEXIT.
        """

        from CommandLine.ext import Syntax
        from termios import tcgetattr
        from sys import stdin, stdout
        from tty import setraw

        settings = self.config
        
        self.__old_settings = tcgetattr(stdin) # store old tty settings

        self.authu() # run authorisation handler

        sx = Syntax(self) # create instance of Syntax class

        while True:
            uinput = ""
            self.__index = 0

            print(end=settings["prompt"])

            while True:
                setraw(stdin) # stop tty from accessing stdin

                char = ord(stdin.read(1))

                if char == 3: # ctrl+c
                    self.reset()
                    print()

                    if settings["interruptexit"]:
                        return settings["atexit"]()
                    else:
                        break
                if char == 5: # ctrl+d
                    self.reset()
                    print()

                    if settings["eofexit"]:
                        return settings["atexit"]()
                    else:
                        return settings["onerror"]()
                elif char in [10, 13]: # enter
                    if sx(uinput, underline=True, valid=True):
                        stdout.write("\r\nechoing... " + uinput + "\n\r")
                        self.reset()
                        print()

                        break
                    else:
                        print(end="\a")
                elif char == 27: # arrow keys
                    next1, next2 = ord(stdin.read(1)), ord(stdin.read(1))

                    if next1 == 91:
                        if next2 == 68: # Left
                            self.__index = max(0, self.__index - 1)
                        elif next2 == 67: # Right
                            self.__index = min(len(uinput), self.__index + 1)
                elif char in range(32, 127):
                    uinput = uinput[:self.__index] + chr(char) + uinput[self.__index:]

                    self.__index += 1
                elif char == 127: # delete
                    uinput = uinput[:self.__index - 1] + uinput[self.__index:]

                    self.__index -= 1

                uinput = sx(uinput, False)

                stdout.write("\r\u001b[0K" + sx(uinput) + "\r" + ("\u001b[" + str(self.__index) + "C" if self.__index > 0 else ""))
                stdout.flush()

                self.reset()

            uin = [s.strip() for s in uinput.split(" ") if s.strip()]

            if not uin:
                continue

            cmd = uin[0]
            args = []
            kwargs = {}

            if len(uin) > 1:
                args = uin[1:]
                
                for a in args:
                    if a.count(":") > 0:
                        l = a.split(":")
                        kwargs[l[0]] = ":".join(l[1:])
                        args.remove(a)

            self.execute(cmd, *args, **kwargs)
