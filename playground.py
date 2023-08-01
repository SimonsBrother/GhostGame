class Obj:
    def __init__(self):
        self.data = "text"


class A:
    def __init__(self):
        self.x = Obj()


class B:
    def __init__(self, a):
        self.x = a.x


a = A()
b = B(a)

print(a.x)
print(b.x)
a.x = Obj()
a.x.data = "not test"
print(a.x)
print(b.x)
