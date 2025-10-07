def multiply(a, b):
    return a * b

def factorial(a):
    for i in range(1, a):
        a = multiply(a, i)
    return a

def int_sqrt(x: int) -> int:
    y = 0
    while y * y <= x:
        y += 1
    return y - 1
