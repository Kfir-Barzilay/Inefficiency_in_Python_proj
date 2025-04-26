import random

class MyKey:
    def __init__(self, x1, x2):
        self.x1 = x1
        self.x2 = x2

    def __hash__(self):
        return hash((self.x1, self.x2))  # tuple hash

    def __eq__(self, other):
        return isinstance(other, MyKey) and self.x1 == other.x1 and self.x2 == other.x2

# Create dict with complex object keys
my_keys = []
my_dict = {}

for _ in range(100000):
    key = MyKey(random.randint(0, 1000000), random.randint(0, 1000000))
    my_keys.append(key)
    my_dict[key] = random.randint(0, 1000000)

# Now force many generic lookups
val = 0
for key in my_keys:
    val ^= my_dict[key]  # XOR
