import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock


@cocotb.test()
async def test_alu_fsm_sequence(dut):
    """Test the full FSM sequence of alu_top.v"""

    # Start 10ns clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize inputs
    dut.in_.value = 0
    dut.opcode.value = 0  # 0 = ADD
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

    # Trigger start
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0  # Pulse for 1 cycle
    await RisingEdge(dut.clk)

    # Confirm transition to LOAD_A_0
    state = int(dut.state_out.value)
    assert state == 1, f"FSM should transition to LOAD_A_0, got {state}"

    # Feed operand A (4 bytes)
    for i in range(4):
        dut.in_.value = i
        await RisingEdge(dut.clk)
        dut._log.info(f"Loaded operand A byte {i}")

    # Feed operand B (4 bytes)
    for i in range(4):
        dut.in_.value = 10 + i
        await RisingEdge(dut.clk)
        dut._log.info(f"Loaded operand B byte {i}")

    # Advance one cycle into EXECUTE
    await RisingEdge(dut.clk)
    dut._log.info(f"State at EXECUTE: {dut.state_out.value.integer}")

    # Advance one more cycle to OUTPUT_0
    await RisingEdge(dut.clk)
    state = int(dut.state_out.value)
    dut._log.info(f"State after EXECUTE: {state}")

    # Check FSM state immediately after EXECUTE
    assert state == 10, f"Expected state OUTPUT_0, got {state}"

    # Check DONE signal at OUTPUT_0
    assert dut.done.value == 1, "Done signal should be high at OUTPUT_0"

    # Read result bytes over 4 cycles
    for i in range(4):
        await RisingEdge(dut.clk)
        byte_value = int(dut.out.value)
        dut._log.info(f"Result byte {i}: {byte_value:02x}")

    # Confirm FSM returns to IDLE
    await RisingEdge(dut.clk)
    state = int(dut.state_out.value)
    assert state == 0, f"FSM should return to IDLE, got {state}"

    dut._log.info("FSM returned to IDLE state successfully")
