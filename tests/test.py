class Base:
    def boo(self):
        print("Base boo")

class Foo(Base):
    def boo(self):
        super().boo()  # Calls Base's boo
        print("Foo boo")

class Too(Foo):
    def boo(self):
        super().boo()  # Calls Foo's boo, which then calls Base's boo
        print("Too boo")

# Testing
too_instance = Too()
too_instance.boo()