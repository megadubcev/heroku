import random
import math


def sum():
    a = random.randint(50, 1000)
    b = random.randint(50, 1000)
    c = a + b
    return [str(a) + " + " + str(b), c]


def raznost():
    a = random.randint(50, 1000)
    b = random.randint(50, 1000)
    c = a + b
    return [str(c) + " - " + str(a), b]


def multiply():
    a = random.randint(3, 15)
    b = random.randint(3, 15)
    c = a * b
    return [str(a) + " * " + str(b), c]


def delenie():
    a = random.randint(3, 15)
    b = random.randint(3, 15)
    c = a * b
    return [str(c) + " / " + str(a), b]


def primer():
    x = random.randint(0, 3)
    if x == 0:
        return sum()
    elif x == 1:
        return raznost()
    elif x == 2:
        return multiply()
    else:
        return delenie()


def uravnenie():
    # uravnenie vida ax + b = cx + d
    x = random.randint(-12, 12)
    c = random.randint(2, 6)
    a = c + random.randint(2, 6)
    dMinusb = x * (a - c)
    b = random.randint(-20, 20)
    d = b + dMinusb
    if b >= 0:
        znak1 = '+'
    else:
        znak1 = '-'

    if d >= 0:
        znak2 = '+'
    else:
        znak2 = '-'

    return [str(a) + "x " + znak1 + ' ' + str(int(math.fabs(b))) + " = " + str(c) + "x " + znak2 + ' ' + str(
        int(math.fabs(d))), x]


def uravnenie2():
    # uravnenie vida ax^2 + bx + c = dx^2 + ex + f
    # x1*x2 = (c - f)/(a-d); -(x1 + x2) = (b-e)/(a-d)
    x1 = random.randint(-2, 2)
    x2 = x1 + random.randint(3, 4)
    d = random.randint(2, 5)
    a = d + random.randint(1, 4)
    cMinusf = x1 * x2 * (a - d)
    eMinusb = (x1 + x2)*(a - d)
    f = random.randint(-5, 5)
    c = cMinusf + f
    b = random.randint(2, 9)
    e = eMinusb + b

    if c >= 0:
        znak1 = '+'
    else:
        znak1 = '-'

    if f >= 0:
        znak2 = '+'
    else:
        znak2 = '-'

    return [str(a) + 'x^2 + ' + str(b) + 'x ' + znak1 + ' ' + str(int(math.fabs(c))) + ' = ' + str(d) + 'x^2 + ' + str(
        e) + 'x ' + znak2 + ' ' + str(int(math.fabs(f))), str(x1) + ' ' + str(x2)]
