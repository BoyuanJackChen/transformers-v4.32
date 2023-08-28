
record = '''n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 1; result is 1.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0
n is 1; c is 0; result is 0.0'''


# Split the record into lines
lines = record.split('\n')

# Initialize a counter
count = 0

# Iterate over the lines
for line in lines:
    # Check if '1' is in the line
    if '1.0' in line:
        count += 1

print(count)
