# benchmark.py
# A sample script with various data types to be analyzed.

# Primitive Types
integer_val = 100
float_val = 3.14
string_val = "hello world"
boolean_val = True
none_val = None

# Data Structures
list_val = [1, 2, "three", 4.0]
tuple_val = (5, "six", 7.0)
dict_val = {"key1": "value1", "key2": 2, 3: "three"}
set_val = {1, 2, 3, 2, 1}

# A simple function
def sample_function(a, b):
    """A simple function to add two numbers."""
    result = a + b
    print(f"Function result: {result}")
    return result

# Using the function
c = sample_function(integer_val, 50)
d = sample_function(float_val, 2.86)

print("Benchmark script has run.")
print(f"List: {list_val}")
print(f"Dictionary: {dict_val}")

