import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock


@cocotb.test()
async def test_alu_fsm_sequence(dut):
    """Test the full FSM sequence of alu_top.v, including operand load, execute, output, and return to IDLE."""

    # Start 10ns clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize inputs
    dut.in_.value = 0
    dut.opcode.value = 0  # 0 = ADD operation
    dut.start.value = 0
    dut.rst_n.value = 1

    await Timer(1, units="ns")

    # Apply reset
    dut._log.info("Applying reset")
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    dut._log.info("Reset complete")

    # Confirm starting in IDLE
    assert dut.state_out.value == 0, "FSM should be in IDLE before start"

    # Step 1: Trigger start in IDLE
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0  # Pulse start for 1 cycle
    await RisingEdge(dut.clk)

    # Step 2: Load operand A (4 bytes)
    for i in range(4):
        dut.in_.value = i
        await RisingEdge(dut.clk)
        dut._log.info(f"Loaded operand A byte {i}")

    # Step 3: Load operand B (4 bytes)
    for i in range(4):
        dut.in_.value = 10 + i
        await RisingEdge(dut.clk)
        dut._log.info(f"Loaded operand B byte {i}")

    # Step 4: Wait for FSM to reach EXECUTE state
    max_cycles = 100
    cycles = 0
    while int(dut.state_out.value) != 9:  # Assuming EXECUTE = 9
        await RisingEdge(dut.clk)
        cycles += 1
        if cycles > max_cycles:
            raise AssertionError("FSM did not reach EXECUTE state in time")
    dut._log.info("FSM reached EXECUTE state")

    # Step 5: Wait for FSM to reach OUTPUT_0
    cycles = 0
    while int(dut.state_out.value) != 10:  # Assuming OUTPUT_0 = 10
        await RisingEdge(dut.clk)
        cycles += 1
        if cycles > max_cycles:
            raise AssertionError("FSM did not reach OUTPUT_0 state in time")

    dut._log.info("FSM reached OUTPUT_0 state")

    # Step 6: Verify DONE signal is asserted at OUTPUT_0
    assert dut.done.value == 1, "Done signal should be high at OUTPUT_0"

    # Step 7: Read result bytes during OUTPUT phases
    result_bytes = []
    for i in range(4):
        await RisingEdge(dut.clk)
        byte_value = int(dut.out.value)
        result_bytes.append(byte_value)
        dut._log.info(f"Result byte {i}: {byte_value:02x}")

    # Step 8: Wait for FSM to return to IDLE
    cycles = 0
    while int(dut.state_out.value) != 0:
        await RisingEdge(dut.clk)
        cycles += 1
        if cycles > max_cycles:
            raise AssertionError("FSM did not return to IDLE after output phase")

    dut._log.info("FSM returned to IDLE state after operation complete")
