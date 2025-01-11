def add(x, y, z):
    z = x + y

if __name__ == "__main__":
    x = 5
    y = 2
    z = 3
    print("before call : ", z)
    add(x, y, z)
    print("after call : ", z)