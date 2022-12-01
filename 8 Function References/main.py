import random
from collections.abc import Callable
def say_hello() -> None:

    print("Hello!")

def say_hello_under_duress() -> None:

    print("I am court-ordered to say hello")

def say_hello_to(name: str) -> None:

    print(f"Hello, {name}!")

def choose_greeting_routine() -> Callable[[],None]:

    choices = [say_hello, say_hello, say_hello_under_duress]
    return random.choice(choices)

greet = say_hello
print(greet)
greet()
greet = say_hello_under_duress
greet()
greet = lambda : say_hello_to("Python")
this = input("waiting")
greet()

greet = choose_greeting_routine()
greet()