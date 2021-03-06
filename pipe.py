#!/usr/bin/env python
""" Infix programming toolkit

Module enabling a sh like infix syntax (using pipes).

= Introduction =
As an exemple, here is the solution for the 2nd Euler Project exercise :

"Find the sum of all the even-valued terms in Fibonacci
 which do not exceed four million."

Given fib a generator of fibonacci numbers :

euler2 = fib() | pwhere(lambda x: x % 2 == 0)
               | ptake_while(lambda x: x < 4000000)
               | padd


= Vocabulary =
 * a Pipe: a Pipe is a 'pipeable' function, somthing that you can pipe to,
           In the code '[1, 2, 3] | add' add is a Pipe
 * a Pipe function: A standard function returning a Pipe so it can be used like
           a normal Pipe but called like in : [1, 2, 3] | concat("#")


= Syntax =
The basic symtax is to use a Pipe like in a shell :
>>> [1, 2, 3] | padd
6

A Pipe can be a function call, for exemple the Pipe function 'where' :
>>> [1, 2, 3] | pwhere(lambda x: x % 2 == 0) #doctest: +ELLIPSIS
[2]

A Pipe as a function is nothing more than a function returning
a specialized Pipe.


= Constructing your own =
You can construct your pipes using Pipe classe initialized with lambdas like :

stdout = Pipe(lambda x: sys.stdout.write(str(x)))
select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))

Or using decorators :
@Pipe
def pstdout(x):
    sys.stdout.write(str(x))

= Existing Pipes in this module =

stdout
    Outputs anything to the standard output
    >>> "42" | pstdout
    42

lineout
    Outputs anything to the standard output followed by a line break
    >>> 42 | plineout
    42

tee
    tee outputs to the standard output and yield unchanged items, usefull for
    debugging
    >>> [1, 2, 3, 4, 5] | ptee | padd
    1
    2
    3
    4
    5
    15

as_list
    Outputs an iterable as a list
    >>> (0, 1, 2) | pas_list
    [0, 1, 2]

as_tuple
    Outputs an iterable as a tuple
    >>> [1, 2, 3] | pas_tuple
    (1, 2, 3)

as_dict
    Outputs an iterable of tuples as a dictionary
    [('a', 1), ('b', 2), ('c', 3)] | pas_dict
    {'a': 1, 'b': 2, 'c': 3}

concat()
    Aggregates strings using given separator, or ", " by default
    >>> [1, 2, 3, 4] | pconcat
    '1, 2, 3, 4'
    >>> [1, 2, 3, 4] | pconcat("#")
    '1#2#3#4'

average
    Returns the average of the given iterable
    >>> [1, 2, 3, 4, 5, 6] | paverage
    3.5

netcat
    Open a socket on the given host and port, and send data to it,
    Yields host reponse as it come.
    netcat apply traverse to its input so it can take a string or
    any iterable.

    "GET / HTTP/1.0\r\nHost: google.fr\r\n\r\n" \
        | pnetcat('google.fr', 80)               \
        | pconcat                                \
        | pstdout

netwrite
    Like netcat but don't read the socket after sending data

pcount
    Returns the length of the given iterable, counting elements one by one
    >>> [1, 2, 3, 4, 5, 6] | pcount
    6

add
    Returns the sum of all elements in the preceding iterable
    >>> (1, 2, 3, 4, 5, 6) | padd
    21

first
    Returns the first element of the given iterable
    >>> (1, 2, 3, 4, 5, 6) | pfirst
    1

chain
    Unfold preceding Iterable of Iterables
    >>> [[1, 2], [3, 4], [5]] | pchain | pconcat
    '1, 2, 3, 4, 5'

    Warning : chain only unfold iterable containing ONLY iterables :
      [1, 2, [3]] | pchain
          Gives a TypeError: chain argument #1 must support iteration
          Consider using traverse

traverse
    Recursively unfold iterables
    >>> [[1, 2], [[[3], [[4]]], [5]]] | ptraverse | pconcat
    '1, 2, 3, 4, 5'
    >>> squares = (i * i for i in range(3))
    >>> [[0, 1, 2], squares] | ptraverse | pas_list
    [0, 1, 2, 0, 1, 4]

select()
    Apply a conversion expression given as parameter
    to each element of the given iterable
    >>> [1, 2, 3] | pselect(lambda x: x * x) | pconcat
    '1, 4, 9'

where()
    Only yields the matching items of the given iterable
    >>> [1, 2, 3] | pwhere(lambda x: x % 2 == 0) | pconcat
    '2'

take_while()
    Like itertools.takewhile, yields elements of the
    given iterable while the predicat is true
    >>> [1, 2, 3, 4] | ptake_while(lambda x: x < 3) | pconcat
    '1, 2'

skip_while()
    Like itertools.dropwhile, skips elements of the given iterable
    while the predicat is true, then yields others
    >>> [1, 2, 3, 4] | pskip_while(lambda x: x < 3) | pconcat
    '3, 4'

chain_with()
    Like itertools.chain, yields elements of the given iterable,
    then yields elements of its parameters
    >>> (1, 2, 3) | pchain_with([4, 5], [6]) | pconcat
    '1, 2, 3, 4, 5, 6'

take()
    Yields the given quantity of elemenets from the given iterable, like head
    in shell script.
    >>> (1, 2, 3, 4, 5) | ptake(2) | pconcat
    '1, 2'

tail()
    Yiels the given quantity of the last elements of the given iterable.
    >>> (1, 2, 3, 4, 5) | ptail(3) | pconcat
    '3, 4, 5'

skip()
    Skips the given quantity of elements from the given iterable, then yields
    >>> (1, 2, 3, 4, 5) | pskip(2) | pconcat
    '3, 4, 5'

islice()
    Just the itertools.islice
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | pislice(2, 8, 2) | pconcat
    '3, 5, 7'

izip()
    Just the itertools.izip
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | pizip([9, 8, 7, 6, 5, 4, 3, 2, 1]) \
            | pconcat
    '(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1)'

aggregate()
    Works as python reduce, the optional initializer must be passed as a
    keyword argument
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | paggregate(lambda x, y: x * y)
    362880

    >>> () | paggregate(lambda x, y: x + y, initializer=0)
    0

    Simulate concat :
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | paggregate(lambda x, y: str(x) + ', ' + str(y))
    '1, 2, 3, 4, 5, 6, 7, 8, 9'

any()
    Returns True if any element of the given iterable satisfies the predicate
    >>> (1, 3, 5, 6, 7) | pany(lambda x: x >= 7)
    True

    >>> (1, 3, 5, 6, 7) | pany(lambda x: x > 7)
    False

all()
    Returns True if all elements of the given iterable
    satisfies the given predicate
    >>> (1, 3, 5, 6, 7) | pall(lambda x: x < 7)
    False

    >>> (1, 3, 5, 6, 7) | pall(lambda x: x <= 7)
    True

max()
    Returns the biggest element, using the given key function if
    provided (or else the identity)

    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | pmax(key=len)
    'qwerty'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | pmax()
    'zoog'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | pmax
    'zoog'

min()
    Returns the smallest element, using the key function if provided
    (or else the identity)

    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | pmin(key=len)
    'b'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | pmin
    'aa'

groupby()
    Like itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)
    (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | pgroupby(lambda x: x % 2 and "Even" or "Odd")
            | pselect(lambda x: "%s : %s" % (x[0], (x[1] | pconcat(', '))))
            | pconcat(' / ')
    'Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8'

sort()
    Like Python's built-in "sorted" primitive. Allows cmp (Python 2.x
    only), key, and reverse arguments. By default sorts using the
    identity function as the key.

    >>> "python" | psort | pconcat("")
    'hnopty'
    >>> [5, -4, 3, -2, 1] | psort(key=abs) | pconcat
    '1, -2, 3, -4, 5'

reverse
    Like Python's built-in "reversed" primitive.
    >>> [1, 2, 3] | preverse | pconcat
    '3, 2, 1'

passed
    Like Python's pass.
    >>> "something" | ppassed
    

index
    Returns index of value in iterable
    >>> [1,2,3,2,1] | pindex(2)
    1
    >>> [1,2,3,2,1] | pindex(1,1)
    4

strip
    Like Python's strip-method for str.
    >>> '  abc   ' | pstrip
    'abc'
    >>> '.,[abc] ] ' | pstrip('.,[] ')
    'abc'

rstrip
    Like Python's rstrip-method for str.
    >>> '  abc   ' | prstrip
    '  abc'
    >>> '.,[abc] ] ' | prstrip('.,[] ')
    '.,[abc'

lstrip
    Like Python's lstrip-method for str.
    >>> 'abc   ' | plstrip
    'abc   '
    >>> '.,[abc] ] ' | plstrip('.,[] ')
    'abc] ] '

run_with
    >>> (1,10,2) | prun_with(range) | pas_list
    [1, 3, 5, 7, 9]

t
    Like Haskell's operator ":"
    >>> 0 | pt(1) | pt(2) == range(3) | pas_list
    True

to_type
    Typecast
    >>> range(5) | padd | pto_type(str) | pt(' is summ!') | pconcat('')
    '10 is summ!'

permutations()
    Returns all possible permutations
    >>> 'ABC' | ppermutations(2) | pconcat(' ')
    "('A', 'B') ('A', 'C') ('B', 'A') ('B', 'C') ('C', 'A') ('C', 'B')"

    >>> range(3) | ppermutations | pconcat('-')
    '(0, 1, 2)-(0, 2, 1)-(1, 0, 2)-(1, 2, 0)-(2, 0, 1)-(2, 1, 0)'

Euler project samples :

    # Find the sum of all the multiples of 3 or 5 below 1000.
    euler1 = (itertools.count() | pselect(lambda x: x * 3) | ptake_while(lambda x: x < 1000) | padd) \
           + (itertools.count() | pselect(lambda x: x * 5) | ptake_while(lambda x: x < 1000) | padd) \
           - (itertools.count() | pselect(lambda x: x * 15) | ptake_while(lambda x: x < 1000) | padd)
    assert euler1 == 233168

    # Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.
    euler2 = fib() | pwhere(lambda x: x % 2 == 0) | ptake_while(lambda x: x < 4000000) | padd
    assert euler2 == 4613732

    # Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
    square = lambda x: x * x
    euler6 = square(itertools.count(1) | ptake(100) | padd) - (itertools.count(1) | ptake(100) | pselect(square) | padd)
    assert euler6 == 25164150


"""
from contextlib import closing
import socket
import itertools
from functools import reduce
import sys

try:
    import builtins
except ImportError:
    import __builtin__ as builtins


__author__ = 'gepcel based on Julien Palard <julien@eeple.fr>'
__credits__ = """Jerome Schneider, for its Python skillz,
and dalexander for contributing"""
__date__ = '09 Dec 2016'
__version__ = '0.1 based on 1.4'
__all__ = [
    'Pipe', 'ptake', 'ptail', 'pskip', 'pall', 'pany', 'paverage', 'pcount',
    'pmax', 'pmin', 'ppermutations', 'pnetcat', 'pnetwrite',
    'ptraverse', 'pconcat', 'pstdout', 'plineout',
    'ptee', 'padd', 'pfirst', 'pchain', 'pselect', 'pwhere', 'ptake_while',
    'pskip_while', 'paggregate', 'pgroupby', 'psort', 'preverse',
    'pchain_with', 'pislice', 'pizip', 'ppassed', 'pindex', 'pstrip', 
    'plstrip', 'prstrip', 'prun_with', 'pt', 'plen', 'pto_type', 'totype',
    'pas_type', 'pastype', 'pas_list', 'pto_list', 
    'paslist', 'ptolist', 'tolist', 'pas_tuple', 'pastuple', 'pto_tuple', 
    'ptotuple', 'pas_dict', 'pasdict', 'pto_dict', 'ptodict', 'pstr', 'ps', 
    'pstre', 'pse', 'ptofile', 'pdump', 'dump', 'pmap', 'phelp', 'pprint',
    'pnt', 'listpipes', 'lp', 'pl', 'pipe'
]

class Pipe:
    """
    Represent a Pipeable Element :
    Described as :
    first = Pipe(lambda iterable: next(iter(iterable)))
    and used as :
    print [1, 2, 3] | first
    printing 1

    Or represent a Pipeable Function :
    It's a function returning a Pipe
    Described as :
    select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))
    and used as :
    print [1, 2, 3] | select(lambda x: x * 2)
    # 2, 4, 6
    """
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return self.function(other)

    def __lt__(self, other):
        return self.function(other)

    def __rrshift__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.function(x, *args, **kwargs))
      
@Pipe
def ptake(iterable, qte):
    "Yield qte of elements in the given iterable."
    for item in iterable:
        if qte > 0:
            qte -= 1
            yield item
        else:
            return

@Pipe
def ptail(iterable, qte):
    "Yield qte of elements in the given iterable."
    out = []
    for item in iterable:
        out.append(item)
        if len(out) > qte:
            out.pop(0)
    return out
        
@Pipe
def pskip(iterable, qte):
    "Skip qte elements in the given iterable, then yield others."
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1

@Pipe
def pall(iterable, pred):
    "Returns True if ALL elements in the given iterable are true for the given pred function"
    return builtins.all(pred(x) for x in iterable)

@Pipe
def pany(iterable, pred):
    "Returns True if ANY element in the given iterable is True for the given pred function"
    return builtins.any(pred(x) for x in iterable)

@Pipe
def paverage(iterable):
    """
    Build the average for the given iterable, starting with 0.0 as seed
    Will try a division by 0 if the iterable is empty...
    """
    total = 0.0
    qte = 0
    for x in iterable:
        total += x
        qte += 1
    return total / qte

@Pipe
def pcount(iterable):
    "Count the size of the given iterable, walking thrue it."
    count = 0
    for x in iterable:
        count += 1
    return count
@Pipe
def plen(iterable):
    return len(iterable)

@Pipe
def pmax(iterable, **kwargs):
    return builtins.max(iterable, **kwargs)

@Pipe
def pmin(iterable, **kwargs):
    return builtins.min(iterable, **kwargs)

@Pipe
def pas_dict(iterable):
    return dict(iterable)

@Pipe
def ppermutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    for x in itertools.permutations(iterable, r):
        yield x

@Pipe
def pnetcat(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | ptraverse:
            s.send(data)
        while 1:
            data = s.recv(4096)
            if not data: break
            yield data

@Pipe
def pnetwrite(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | ptraverse:
            s.send(data)

@Pipe
def ptraverse(args):
    for arg in args:
        try:
            if isinstance(arg, str):
                yield arg
            else:
                for i in arg | ptraverse:
                    yield i
        except TypeError:
            # not iterable --- output leaf
            yield arg

@Pipe
def pconcat(iterable, separator=", "):
    return separator.join(map(str,iterable))

@Pipe
def pas_list(iterable):
    return list(iterable)

@Pipe
def pas_tuple(iterable):
    return tuple(iterable)

@Pipe
def pstdout(x):
    sys.stdout.write(str(x))

@Pipe
def plineout(x):
    sys.stdout.write(str(x) + "\n")

@Pipe
def ptee(iterable):
    for item in iterable:
        sys.stdout.write(str(item) + "\n")
        yield item

@Pipe
def padd(x):
    return sum(x)

@Pipe
def pfirst(iterable):
    return next(iter(iterable))

@Pipe
def pchain(iterable):
    return itertools.chain(*iterable)

@Pipe
def pselect(iterable, selector):
    return [selector(x) for x in iterable]

@Pipe
def pwhere(iterable, predicate):
    return [x for x in iterable if (predicate(x))]

@Pipe
def ptake_while(iterable, predicate):
    return itertools.takewhile(predicate, iterable)

@Pipe
def pskip_while(iterable, predicate):
    return itertools.dropwhile(predicate, iterable)

@Pipe
def paggregate(iterable, function, **kwargs):
    if 'initializer' in kwargs:
        return reduce(function, iterable, kwargs['initializer'])
    else:
        return reduce(function, iterable)
@Pipe
def pgroupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)

@Pipe
def psort(iterable, **kwargs):
    return sorted(iterable, **kwargs)

@Pipe
def preverse(iterable):
    return reversed(iterable)

@Pipe
def ppassed(x):
    pass

@Pipe
def pindex(iterable, value, start=0, stop=None):
    return iterable.index(value, start, stop or len(iterable))

@Pipe
def pstrip(iterable, chars=None):
    return iterable.strip(chars)

@Pipe
def prstrip(iterable, chars=None):
    return iterable.rstrip(chars)

@Pipe
def plstrip(iterable, chars=None):
    return iterable.lstrip(chars)

@Pipe
def prun_with(iterable, func):
    return  func(**iterable) if isinstance(iterable, dict) else \
            func( *iterable) if hasattr(iterable,'__iter__') else \
            func(  iterable)

@Pipe
def pt(iterable, y):
    if hasattr(iterable,'__iter__') and not isinstance(iterable, str):
        return iterable + type(iterable)([y])
    else:
        return [iterable, y]

@Pipe
def pto_type(x, t):
    return t(x)


pchain_with = Pipe(itertools.chain)
pislice = Pipe(itertools.islice)

# Python 2 & 3 compatibility
if "izip" in dir(itertools):
    pizip = Pipe(itertools.izip)
else:
    pizip = Pipe(zip)


# print the result
pnt = pprint = Pipe(print)

# convert the result to str
pstr = Pipe(str)
@Pipe
def pstre(x):
    if hasattr(x,'__iter__') and not isinstance(x, str):
        if type(x) is range:
            tp = list
        else:
            tp = type(x)
        return tp(map(str, x))
    else:
        return str(x)
pse = pstre

ps = pstr = Pipe(str)

# dump the result to file
@Pipe
def ptofile(x, filename=None, override=False, encoding=None,
     sep=''):
    if filename:
        if override: 
            mode='w'
        else:
            print("File already exists, add to the end")
            mode='a'
    if not filename:
        import os
        filename = os.path.join(os.getcwd(), 'temptxtfile.txt')
        mode='w'
    with open(filename, mode, encoding=encoding) as file:
        if hasattr(x,'__iter__') and not isinstance(x, str):
            x = map(str, x)
            file.write(sep.join(x))
        else:
            file.write(str(x))
dump = pdump = ptofile

@Pipe
def pmap(x, f):
    tp = type(x)
    if tp is range:
        tp = list
    return tp(map(f, x))

phelp = Pipe(help) # not of much use

@Pipe
def pipe(arg, func, *args, **kwargs):
    '''
    Just pipe anything to any function with any parameters
    '''
    return func(arg, *args, **kwargs)

@Pipe
def listpipes(x):
    print([
    'Pipe', 'ptake', 'ptail', 'pskip', 'pall', 'pany', 'paverage', 'pcount',
    'pmax', 'pmin', 'ppermutations', 'pnetcat', 'pnetwrite',
    'ptraverse', 'pconcat', 'pas_list', 'pas_tuple', 'pstdout', 'plineout',
    'ptee', 'padd', 'pfirst', 'pchain', 'pselect', 'pwhere', 'ptake_while',
    'pskip_while', 'paggregate', 'pgroupby', 'psort', 'preverse',
    'pchain_with', 'pislice', 'pizip', 'ppassed', 'pindex', 'pstrip', 
    'plstrip', 'prstrip', 'prun_with', 'pt', 'plen', 
    'pto_type--totype--pas_type--pastype', 
    'pas_list--pto_list--paslist--ptolist--tolist', 
    'pas_tuple--pastuple--pto_tuple--ptotuple', 
    'pas_dict--pasdict--pto_dict--ptodict', 
    'pstr--ps', 'pstre--pse', 'ptofile--pdump--dump', 'pmap', 'phelp', 
    'pnt--pprint', 'pl--lp--listpipes', 'pipe'
])

# aliases
pl = lp = listpipes

pas_type = pto_type
ptotype = pto_type
pastype = pto_type
totype = pto_type # because totype is used too much

pto_dict = pas_dict
ptodict = pas_dict
pasdict = pas_dict

pto_list = pas_list
ptolist = pas_list
paslist = pas_list
tolist = pas_list  # because tolist is used too much

pto_tuple = pas_tuple
ptotuple = pto_tuple
pastuple = pas_tuple

if __name__ == "__main__":
    import doctest
    doctest.testmod()
