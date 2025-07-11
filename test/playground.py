import struct

def float_to_binary(f):
    """Converts a float to its 32-bit binary representation."""
    # Pack the float into 4 bytes (single-precision)
    packed_bytes = struct.pack('>f', f)  # '>f' for big-endian float
    # Convert the bytes to an integer

    integer_representation = int.from_bytes(packed_bytes, 'big')
    # Format the integer as a 64-bit binary string
    binary_string = format(integer_representation, '032b')
    binary_string = binary_string[0] + " " + binary_string[1:9] + " " + binary_string[9:]
    return binary_string

# Helper function: convert Python float to 32-bit IEEE 754 bit pattern (as an integer)
def float_to_bits(f):
    return struct.unpack('>I', struct.pack('>f', f))[0]

# Helper function: convert 32-bit IEEE 754 bit pattern to Python float (as an integer)
def bits_to_float(b):
    return struct.unpack('>f', struct.pack('>I', b))[0]

print(float_to_binary(-1.234e-41))
print(float_to_bits(-1.234e-41))
print(bits_to_float(float_to_bits(-1.234e-41)))