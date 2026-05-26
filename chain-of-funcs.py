def add(x):
    result = x + 10
    def multi(y):
        def div(z):
            return z / 10
        return div(y * 10)
    return multi(result)

assert add(10) == 20