n = 18
k = 13

chunk_size = n // k  # integer division
remainder = n % k
elements = [chunk_size] * k
# Distribute the remainder over the first few elements
for i in range(remainder):
    elements[i] += 1
print(elements)
