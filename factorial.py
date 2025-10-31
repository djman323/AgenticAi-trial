"""This program calculates the factorial of a number."""

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

num = 5 # Change this number to calculate the factorial of a different number
result = factorial(num)
print(f"The factorial of {num} is {result}")