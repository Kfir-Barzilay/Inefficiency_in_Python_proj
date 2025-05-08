my_dict = {}
for i in range(2**16 - 1):
    first_8 = (i >> 8) & 0xFF       # Extract the top 8 bits
    last_8 = i & 0xFF               # Extract the bottom 8 bits
    my_key = (first_8, last_8)      # Create tuple key
    my_dict[my_key] = i

print(my_dict[(41,89)])

