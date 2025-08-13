# 类和对象
# 学习面向对象编程

class Person:
    """人类"""
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        print(f"Hi, my name is {self.name} and I am {self.age} years old.")

# 创建对象
alice = Person("Alice", 25)
alice.greet()