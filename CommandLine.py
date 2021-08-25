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

    def exit(self, status="0"):
        """
        If status is 0 (default), the commandline exits by calling
ATEXIT. If status is an integer, the commandline will exit by
calling system.exit() with that integer If status is a string, this
will be printed and the exit status will be 1 (i.e., failure).
Args:
        status[optional]: The exit status
        """
        from sys import exit as __exit

        settings = self.config

        if status == "0":
            settings["atexit"]()
        elif status.isdigit():
            __exit(int(status))

        return print(status) or status

    def help(self, command=""):
        """
        Prints every command and how to use them.
Args:
        command[optional]: The name of the command to get help on
        """

        for _n, _f in self.__commands.items(): # self.__commands is a dict of commands names and functions
            _f_docs = ""

            if _f.__doc__:
                _f_docs = "\n\t".join(_f.__doc__.strip().split("\n")) # reformat the function's doc strings

            _f_args = []

            for _attr in _f.__code__.co_varnames: # for each local variable in the function
                if _attr[0] != "_" and _attr != "settings": # if it is not named settings or starts with a '_'
                    _f_args += [_attr] # add it to the list of variables

            _f_args = ", ".join(_f_args) # then format that list

            print(f"\r{_n}({_f_args}):\n\n\r\t{_f_docs}\n") # print it all out nicely

    def hi(self):
        """
        Prints "hi"
Args:
        -
        """

        print("hi")

    @property
    def __commands(self):
        attrs = [attr for attr in self.__dir__() if not attr[0] == "_"]

        return {attr:self.__getattribute__(attr) for attr in attrs if callable(self.__getattribute__(attr))} # returns a dict of functions not starting with '_', and their names

    def __execute(self, name: str, *args, **kwargs):
        settings = self.config

        if name not in self.__commands: # if name is not a valid command
            if settings["onerror"] == exit:
                raise KeyError("Function not found.") # raise an error if the settings say that is allowed
            else:
                return settings["onerror"]() # otherwise return the ouput on error func

        return self.__commands[name](*args, **kwargs) # return the output of the command

    def __call__(self):
        settings = self.config

        while True:
            try:
                uin = input(settings["prompt"])
                ans = [s.strip() for s in uin.split(" ") if s.strip()]
            except EOFError as E:
                if settings["eofexit"]:
                    settings["atexit"]()
                else:
                    raise EOFError()
            except KeyboardInterrupt as E:
                if settings["interruptexit"]:
                    settings["atexit"]()
                else:
                    raise KeyboardInterrupt()
            except Exception:
                settings["onerror"]()

            if not ans:
                continue

            cmd = ans[0]
            args = []
            kwargs = {}

            if len(ans) > 1:
                args = ans[1:]
                
                for a in args:
                    if a.count(":") > 0:
                        l = a.split(":")
                        kwargs[l[0]] = ":".join(l[1:])
                        args.remove(a)

            self.__execute(cmd, *args, **kwargs)


if __name__ == "__main__":
    from subprocess import run, DEVNULL, STDOUT
    from os import system
    
    try:
        run(["ls", "/dev/null"], stdout=DEVNULL, stderr=STDOUT)
        system("clear")
    except FileNotFoundError:
        system("cls")

    print("Ready!")

    cmdln = CommandLine(atexit=exit, onerror=exit, prompt="> ", eofexit=True, interruptexit=True)
    cmdln()