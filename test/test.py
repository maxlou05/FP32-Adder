# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadWrite

import struct


PERIOD = 1000  # Clock period in ns


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Start the clock
    clock = Clock(dut.clk, PERIOD, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)

    assert dut.state_out.value.integer == 0, "FSM should be in IDLE before start"
    assert dut.done.value == 0
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Begin the test by inputting start (indicate to ALU that we want to start inputting numbers)
    dut.uio_in.value = BinaryValue("0x1zzzzz")  # Set io[0] = 0 for add, leave the output ones to be driven by design

    await RisingEdge(dut.clk)
    await ReadWrite()

    # Numbers to add
    a = 1.234
    b = 5.678
    expected = a + b

    # Load operand A
    for i in range(4):
        dut.uio_in.value = struct.pack("<f", a)[i]  # Put in little endian to input byte 0 first
        await RisingEdge(dut.clk)
        await ReadWrite()

    # Load operand B
    for i in range(4):
        dut.uio_in.value = struct.pack("<f", b)[i]
        await RisingEdge(dut.clk)
        await ReadWrite()

    # Wait for execute
    await RisingEdge(dut.clk)
    await ReadWrite()

    # Read outputs
    result = bytearray([0, 0, 0, 0])
    for i in range(4):
        result[i] = dut.uo_out.value.integer
        assert dut.done.value == 1
        await RisingEdge(dut.clk)
        await ReadWrite()

    final_number = struct.unpack("<f", result)[0]
    temp = struct.unpack(">f", result)[0]
    assert abs(final_number - expected) < 1e-6, f"Addition failed: {a} + {b} != {final_number}. {result=}, big-endian:{temp}"
