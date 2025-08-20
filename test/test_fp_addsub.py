import math
import random
import struct                                  # For float <-> binary conversion

import cocotb                                  # Main Cocotb library
from cocotb.triggers import Timer              # For time-based delays


PERIOD = 40  # clock period in ns


# NOTE: cocotb handles the endianness issue, so 240 = 0x00 FF = 00000000 11111111 is inputted as a[16..0] = 00000000 11111111, and not a[16..0] = 11111111 00000000 due to little endianness represents it as 0xFF 00 in memory
# Helper function: convert Python float to 32-bit IEEE 754 bit pattern (as an integer)
def float_to_bits(f) -> int:
    return struct.unpack('>I', struct.pack('>f', f))[0]

# Helper function: convert 32-bit IEEE 754 bit pattern (as an integer) to Python float
def bits_to_float(b) -> float:
    return struct.unpack('>f', struct.pack('>I', b))[0]

# Test adding numbers
@cocotb.test()
async def test_add(dut):
    a, b = 1.25, 2.75             # Input floats
    expected = a + b              # Expected result

    dut.a.value = float_to_bits(a)  # Apply float A in IEEE 754 bit form
    dut.b.value = float_to_bits(b)  # Apply float B in IEEE 754 bit form
    dut.sub.value = 0               # 0 = add

    await Timer(PERIOD, units='ns')      # Wait for result to settle
    result = bits_to_float(dut.result.value.integer)  # Convert result back to float
    assert abs(result - expected) < 1e-6, f"positive + positive failed: {a} + {b} != {result}"

    a, b = math.pi, -math.e
    expected = a + b
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"positive + negative failed: {a} + {b} != {result}"

    a, b = -2.0, 3.0
    expected = a + b
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"negative + positive failed: {a} + {b} != {result}"

    a, b = -4.67e-3, -3.14
    expected = a + b
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"negative + negative failed: {a} + {b} != {result}"

# Test subtracting numbers
@cocotb.test()
async def test_sub(dut):
    a, b = 5.5, 3.25              # Input floats
    expected = a - b              # Expected result

    dut.a.value = float_to_bits(a)  # Apply A
    dut.b.value = float_to_bits(b)  # Apply B
    dut.sub.value = 1               # 1 = subtract

    await Timer(PERIOD, units='ns')      # Wait for result
    result = bits_to_float(dut.result.value.integer)  # Read output
    assert abs(result - expected) < 1e-6, f"positive - positive failed: {a} - {b} != {result}"

    a, b = math.pi, -math.e
    expected = a - b
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"positive - negative failed: {a} - {b} != {result}"

    a, b = -142.5, 32.89
    expected = a - b
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"negative - positive failed: {a} - {b} != {result}"

    a, b = -4.67e-3, -3.14
    expected = a - b
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"negative - negative failed: {a} - {b} != {result}"

# Test arithmetic with 0
@cocotb.test()
async def test_zero_add(dut):
    a, b = 0.0, 5.0
    expected = a + b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"Zero add failed: {a} + {b} != {result}"

@cocotb.test()
async def test_zero_sub(dut):
    a, b = 0.0, 5.0
    expected = a - b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"Zero sub failed: {a} - {b} != {result}"

@cocotb.test()
async def test_add_zero(dut):
    a, b = 5.0, 0.0
    expected = a + b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"Add zero failed: {a} + {b} != {result}"

@cocotb.test()
async def test_sub_zero(dut):
    a, b = 5.0, 0.0
    expected = a - b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"Subtract zero failed: {a} - {b} != {result}"

@cocotb.test()
async def test_add_to_zero(dut):
    a, b = 5.0, -5.0
    expected = 0.0

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Add to zero failed: {a} + {b} != {result}"

@cocotb.test()
async def test_sub_to_zero(dut):
    a, b = 5.0, 5.0
    expected = 0.0

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Subtract to zero failed: {a} - {b} != {result}"

# Testing rounding cut-off (underflow)
@cocotb.test()
async def test_rounding(dut):
    a, b = 1.0, 1e-10

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == 1.0, f"Rounding failed: should have rouded off due to large descrepancy in exponent, but got {result}"

# Test carry over to increase exponent
@cocotb.test()
async def test_increase_exponent(dut):
    a, b = 8.0, 8.0
    expected = a + b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"Increase exponent failed: {a} + {b} != {result}"

# Test decrease exponent
@cocotb.test()
async def test_decrease_exponent(dut):
    a, b = 8.0, 6.0
    expected = a - b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-6, f"Decrease exponent failed: {a} - {b} != {result}"

# Test add 2 subnormal numbers
@cocotb.test()
async def test_both_subnormals(dut):
    a, b = 1.234e-41, 5.678e-41  # 10^-41 is less than 2^-127, which is subnormal
    expected = a + b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-44, f"Add 2 subnormal numbers failed: {a} + {b} != {result}"

    expected = a - b
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-44, f"Subtract 2 subnormal numbers failed: {a} - {b} != {result}"

# Test when the result is a subnormal number
@cocotb.test()
async def test_sub_become_subnormals(dut):
    a, b = 3.52e-38, 3.51e-38
    expected = a - b  # 10^-40 is less than 2^-127

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-40, f"Normalized numbers subtract to obtain subnormal number failed: {a} - {b} != {result}"

# Test add a subnormal number to a normalized number
@cocotb.test()
async def test_add_subnormal_to_normal(dut):
    a, b = -4.67e-41, 3.4124e-37
    expected = a + b

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert abs(result - expected) < 1e-43, f"Add subnormal number to normalized number failed: {a} + {b} != {result}"

# Test Infinities
@cocotb.test()
async def test_result_positive_infinity(dut):
    expected = float("inf")

    a, b = float("inf"), 1242.2362642
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Add finite number to infinity failed: {a} + {b} != {result}"

    a, b = 6523.1235, float("-inf")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Subtract -infinity failed: {a} - {b} != {result}"

    a, b = float("inf"), float("-inf")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Infinity + infinity failed: {a} - {b} != {result}"

@cocotb.test()
async def test_result_negative_infinity(dut):
    expected = float("-inf")

    a, b = float("-inf"), 9823.14
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Add finite number to -infinity failed: {a} + {b} != {result}"

    a, b = 2601.361, float("inf")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"Subtract infinity failed: {a} - {b} != {result}"

    a, b = float("-inf"), float("-inf")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"-Infinity - infinity failed: {a} + {b} != {result}"

@cocotb.test()
async def test_overflow_become_infinity(dut):
    a, b = 2.4e38, 3.1e38  # Max value for 32-bit float is around 3.4e38
    expected = float("inf")

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"positive overflow to infinity failed: {a} + {b} != {result}"

    a, b = -2.4e38, 3.1e38  # Max value for 32-bit float is around 3.4e38
    expected = float("-inf")

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert result == expected, f"negative overflow to infinity failed: {a} + {b} != {result}"

# Test NaNs
@cocotb.test()
async def test_input_nan(dut):
    expected = float("nan")

    a, b = float("-nan"), 9823.14
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    # Use str() since NaN == NaN evaluates to False
    assert str(result) == str(expected), f"Add finite number to -infinity failed: {a} + {b} != {result}"

    a, b = 2601.361, float("nan")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Subtract infinity failed: {a} - {b} != {result}"

    a, b = float("nan"), float("nan")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"-Infinity - infinity failed: {a} + {b} != {result}"

@cocotb.test()
async def test_infinity_sub_infinity(dut):
    expected = float("nan")

    a, b = float("inf"), float("inf")
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1
    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"infinity - infinity failed: {a} - {b} != {result}"

# Test signed zeros
# NOTE: Not really possible to test underflow (i.e. the result is something smaller than a floating point number can represent, very close to 0)
# due to requiring the input to then have more precision than a floating point itself
@cocotb.test()
async def test_result_positive_zero(dut):
    a, b = 0.0, 0.0
    expected = 0.0

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    # Use str() since 0.0 == -0.0 evaluates to True
    assert str(result) == str(expected), f"Result should have been positive zero: {a} + {b} != {result}"

    a, b = 0.0, 0.0
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been positive zero: {a} - {b} != {result}"

    a, b = 0.0, -0.0
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been positive zero: {a} + {b} != {result}"

    a, b = 0.0, -0.0
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been positive zero: {a} - {b} != {result}"

    a, b = -0.0, 0.0
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been positive zero: {a} + {b} != {result}"

    a, b = -0.0, -0.0
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been positive zero: {a} - {b} != {result}"

@cocotb.test()
async def test_result_negative_zero(dut):
    a, b = -0.0, -0.0
    expected = -0.0

    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 0

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been negative zero: {a} + {b} != {result}"

    a, b = -0.0, 0.0
    dut.a.value = float_to_bits(a)
    dut.b.value = float_to_bits(b)
    dut.sub.value = 1

    await Timer(PERIOD, units='ns')
    result = bits_to_float(dut.result.value.integer)
    assert str(result) == str(expected), f"Result should have been positive zero: {a} - {b} != {result}"


# Random test
MIN_SUBNORMAL_VAL = 1.40e-45  # 1.40129845e-45 is min float, MIN_VAL < min float. So x < MIN_VAL => x < min float
MIN_NORMAL_VAL = 1.175494e-38
MAX_VAL = 3.4028235e+38  # 3.402823466 is max float, MAX_VAL > max float. So x > MAX_VAL => x > max float
def generate_random_f32() -> float:
    while True:
        x = random.uniform(1, 10)
        x *= 10**random.randint(-45, 38)
        x = -x if random.randint(0, 1) == 1 else x
        if x == 0.0 or (abs(x) > MIN_SUBNORMAL_VAL and abs(x) < MAX_VAL):
            break
    return x

COUNT = 1000000
@cocotb.test()
async def test_random_operations(dut):
    for _ in range(COUNT):
        a = generate_random_f32()
        b = generate_random_f32()
        operation = random.randint(0, 1)
        expected = a - b if operation == 1 else a + b

        dut.a.value = float_to_bits(a)
        dut.b.value = float_to_bits(b)
        dut.sub.value = operation

        await Timer(PERIOD, units='ns')
        result = bits_to_float(dut.result.value.integer)

        if abs(expected) > MAX_VAL:
            dut._log.info(f"Overflow detected: {a} {'-' if operation == 1 else '+'} {b}")
            assert "inf" in str(result), f"Overflow detection failed: {a} {'-' if operation == 1 else '+'} {b} != {result}"
        elif abs(expected) < MIN_SUBNORMAL_VAL:
            dut._log.info(f"Underflow detected {a} {'-' if operation == 1 else '+'} {b}")
            assert abs(result) == 0.0 or abs(result - expected) < MIN_SUBNORMAL_VAL, f"Underflow detection failed: {a} {'-' if operation == 1 else '+'} {b} != {result}"
        else:
            assert abs(result - expected) < max(max(abs(a), abs(b)) * 1e-6, MIN_SUBNORMAL_VAL * 2), f"Operation failed: {a} {'-' if operation == 1 else '+'} {b} != {result}"
