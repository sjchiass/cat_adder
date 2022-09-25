# Convert a string of numbers joined by +s into a list of 8-bit integers
def sum_parse(s):
    return [to_bits(n) for n in s.split("+")]

# Convert a number into an 8-bit integer
def to_bits(n):
    # Convert the input into a real integer
    n = int(n)
    # Prepare a 0 list
    answer = 8*[0]
    # Test each bit, from the largest to the smallest
    for x in reversed(range(8)):
        # If bit's ON value is greater or equal to the integer, activate
        # the bit and subtract from the integer
        if n >= 2**x:
            n -= 2**x
            answer[7-x] = 1
    return answer

# Sum all of the lists together
def sum_lists(lists):
    # Initialize an empty list
    answer = [0]*8
    # Set the remainder to 0
    remainder = 0
    # Since the least significant bit is to the right, the loop has to 
    # start from the end and work its way to 0
    for i in reversed(range(8)):
        # For each list, read its bit value and add it
        for l in lists:
            answer[i] += l[i]
        # Add the remainder to the running total
        answer[i] += remainder
        # Calculate how much of the answer is the remainder
        # (This is like an AND operation over bits)
        remainder = answer[i] // 2
        # Calculate the final value for the current bit
        # (This is like a XOR operation over bits)
        answer[i] = answer[i] % 2
    return answer

# Convert a list of bits into a number
def from_bits(l):
    # Work from the end back to 0
    l = reversed(l)
    x = 0
    for n, i in enumerate(l):
        # Each bit is worth 2^n, if it's set to 1
        x += i*2**n
    return x

while True:
    print(
        from_bits(
            sum_lists(
                sum_parse(
                    input()))))
