def HasValues(dict, *args):
    for arg in args:
        if arg not in dict:
            return False
    return True
class staticproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func()