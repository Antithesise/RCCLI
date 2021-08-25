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

    def command(self):
        def decorator_command(func):
            from functools import wraps

            @wraps(func)
            def wrapper_command(*args, **kwargs):
                from os import environ

                if self.auth == environ["CODE"]:
                    return func(*args, **kwargs)
                else:
                    raise PermissionError("You haven't been authorised yet")
            return wrapper_command
        return decorator_command

    @property
    def commands(self):
        attrs = [attr for attr in self.__dir__() if not attr[0] == "_"]

        return {attr:self.__getattribute__(attr) for attr in attrs if callable(self.__getattribute__(attr))} # returns a dict of functions not starting with '_', and their names

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

    def __call__(self):
        settings = self.config

        while True:
            try:
                uin = input(settings["prompt"])
                ans = [s.strip() for s in uin.split(" ") if s.strip()]
            except EOFError as E:
                if settings["eofexit"]:
                    return settings["atexit"]()
                else:
                    raise EOFError()
            except KeyboardInterrupt as E:
                if settings["interruptexit"]:
                    return settings["atexit"]()
                else:
                    raise KeyboardInterrupt()
            except Exception:
                return settings["onerror"]()

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

            self.execute(cmd, *args, **kwargs)
