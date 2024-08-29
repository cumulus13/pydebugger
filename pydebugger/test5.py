import inspect

class Test:
    
    @classmethod
    def printlist(cls, *args, **kwargs):
        caller_locals = inspect.currentframe().f_back.f_locals
        
        printed = False
        print("args = ", args)
        print("kwargs = ", kwargs)
        
        for arg in args:
            if isinstance(arg, str):
                found = False
                for name, value in caller_locals.items():
                    if arg == name or arg == value:
                        found = True
                        print(f"{name} [1] = {value}")
                        printed = True
                        break
                if not found:
                    printed = True
                    print(f"start {arg} ..........")
            else:
                variables = [name for name, value in caller_locals.items() if value == arg]
                if variables:
                    printed = True
                    for name in variables:
                        print(f"{name} [2] = {arg}")

        if not printed:
            print("No matching variables or functions found.")

    @classmethod
    def test1(cls):
        return "test1"

    @classmethod
    def test2(cls):
        return "test2"

    @classmethod
    def test3(cls):
        return "test3"

data1 = Test.test1()
data2 = Test.test2()
data3 = Test.test3()

Test.printlist(data1, data2, data3, 'data4')
