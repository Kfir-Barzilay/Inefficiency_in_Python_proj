def my_add_function(x , y):
    if x > y:
        return 2 * x + y
    elif x < y:
        return x + 2 * y
    else:
        return x + y
    
print (my_add_function(5 , 3))
print (my_add_function(3 , 5))
print (my_add_function(4 , 4))