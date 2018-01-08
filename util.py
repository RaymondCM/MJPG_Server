from sys import platform


def is_linux():
    return platform == "linux" or platform == "linux2"


def is_windows():
    return platform == "win32" or platform == "cygwin"


def is_osx():
    return platform == "darwin"


def is_bsd():
    return platform == "freebsd7" or platform == "freebsd8" or platform == "freebsdN"


def raspberrypi():
    return "pi"


def thermal():
    return "lepton"


def default():
    return "cv"


def lepton_in(modules):
    return "pylepton.Lepton3" in modules
