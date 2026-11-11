i = [5]

def f(arg=i):
    print(arg)
    arg.append(1)

i = [5,1]

f()
f()
f()


#[5]
#[5, 1]
#[5, 1, 1]
