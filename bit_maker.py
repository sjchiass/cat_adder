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

while True:
    print(sum_parse(input()))
