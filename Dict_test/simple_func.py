def my_add_function(x , y):
    if x > y:
        return 2 * x + y
    elif x < y:
        return x + 2 * y
    else:
        return x + y
sum = 0    
for i in range (10**5):
    sum += my_add_function(i , i)
    sum += my_add_function(i , i+1)
    sum += my_add_function(i+1 , i)

print("My sum is:" + sum)