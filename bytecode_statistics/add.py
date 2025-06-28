import dis
def add(a, b):
    return a + b


dis.dis(add)

def main():
    print(add(4, 5))
    print(add(6, 7))
    print(add(8, 9))



if __name__ == '__main__':
    main()
