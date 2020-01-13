import unittest

from satella.coding import static_var


class FunTestTest(unittest.TestCase):
    def test_fun_static_function(self):
        @static_var("counter", 2)
        def static_fun(a):
            static_fun.counter += 1
            return a

        static_fun(2)
        static_fun(3)
        self.assertEqual(static_fun.counter, 4)

    def test_fun_static_method(self):
        class MyClass(object):
            @static_var("counter", 2)
            def my_method(self):
                MyClass.my_method.counter += 1
                return a

        a = MyClass()
        a.my_method()
        a.my_method()
        self.assertEqual(MyClass.my_method.counter, 4)
