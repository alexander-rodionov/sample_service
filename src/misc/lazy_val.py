class LazyValue:
    def __init__(self, param):
        if callable(param):
            self.func = param
            self.val = None
        else:
            self.val = param

    def __call__(self, *args, **kwargs):
        if self.val is None:
            self.val = self.func(*args, **kwargs)
        return self.val
