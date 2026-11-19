def collect(value, buffer=None):
    if buffer is None:
        buffer = []
    buffer.append(value)
    return buffer

print(collect(0.1))
print(collect(0.2))
