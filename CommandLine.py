class CommandLine:
    def __init__(self, **config):
        self.config = {k.lower():v for k, v in config.items()} # self.config = config, but all keys are loweraces

        defaults = { # default configuration settings
            "atexit": exit,
            "onerror": exit,
            "prompt": "> ",
            "eofexit": True,
            "interruptexit": True,
        }

        for k in defaults.keys(): # for each configuration setting
            if k not in self.config: # if user hasn't specified that specific setting
                self.config[k] = defaults[k] # set that setting to the default
                
                if k == "onerror" and k not in defaults: # if atexit is set and onerror isn't
                    self.config[k] = self.config["atexit"] # set onerror to atexit
        
        self.commands = {}

    def reset(self):
        from termios import tcsetattr, TCSADRAIN
        from sys import stdin

        tcsetattr(stdin.fileno, TCSADRAIN, self.__old_settings)

    def command(self, *args, **kwargs):
        def decorator_command(func):
            from functools import wraps

            self.commands[func.__name__] = func

            @wraps(func)
            def wrapper_command(*args, **kwargs):
                from os import environ

                if self.auth == environ["CODE"]:
                    return func(*args, **kwargs)
                else:
                    raise PermissionError("You haven't been authorised yet")
            return wrapper_command
        return decorator_command

    def execute(self, name: str, *args, **kwargs):
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
                raise TypeError("Too many arguments given.")
            else:
                return settings["onerror"]()

    def run(self, auth=None):
        self.auth = auth
        self()

    def __call__(self):
        from termios import tcgetattr
        from sys import stdin, stdout
        from Getpass import getpass
        from Syntax import Syntax
        from tty import setraw
        from os import getenv

        settings = self.config

        while self.auth != getenv("CODE"):
            self.auth = getpass("Password: ")
            if self.auth == getenv("CODE"):
                break
            print("Incorrect!")

        self.__syntax = self.Syntax(self) # create instance of Syntax class
        self.__old_settings = tcgetattr(stdin) # store old tty settings

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
                        raise EOFError()
                elif char in [10, 13]: # enter
                    if self.__syntax(uinput, underline=True, valid=True):
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

                uinput = self.__syntax(uinput, False)

                stdout.write("\r\u001b[0K" + self.__syntax(uinput) + "\r" + ("\u001b[" + str(self.__index) + "C" if self.__index > 0 else ""))
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
