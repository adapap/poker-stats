import csv
import io
import random
import pprint


def concatenate(file):
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.reader(stream)
    names = []

    for r in reader:
        names += r

    stream.close()
    del names[0]
    return names


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

L = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
random.shuffle(L)
print(L)
pprint.pprint(list(chunks(L, 3)))

