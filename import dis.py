import dis

dict = {}

def example(a,b):
    return a+b

def get_item(key, dict):
    return dict[key]


dis.dis(get_item)