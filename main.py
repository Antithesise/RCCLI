from CommandLine import CommandLine

cmdln = CommandLine(atexit=exit, onerror=exit, prompt="> ", eofexit=True, interruptexit=True)

cmdln()