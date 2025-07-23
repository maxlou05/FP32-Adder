import cocotb
from cocotb.triggers import RisingEdge, ReadWrite
from cocotb.clock import Clock


PERIOD = 40  # clock period in ns


@cocotb.test()
async def test_alu_fsm_sequence(dut):
    """Test the full FSM sequence of alu_top.v"""

    # Start a clock on dut.clk
    cocotb.start_soon(Clock(dut.clk, PERIOD, units="ns").start())

    # Initialize all inputs (reset)
    dut.in_.value = 0
    dut.opcode.value = 0  # 0 = add
    dut.start.value = 0
    dut.rst_n.value = 0

    # Apply reset
    dut._log.info("Applying reset")

    await RisingEdge(dut.clk)

    # Stop the reset
    dut.rst_n.value = 1

    await RisingEdge(dut.clk)
    await ReadWrite()
    dut._log.info("Reset complete")

    # Step 1: Trigger start in IDLE (write high for 1 cycle)
    assert dut.state_out.value.integer == 0, "FSM should be in IDLE before start"
    assert dut.done.value == 0
    dut.start.value = 1

    await RisingEdge(dut.clk)
    await ReadWrite()

    # Stop the start pulse
    dut.start.value = 0

    # Step 2: Feed operand A (4 bytes)
    for i in range(4):
        dut.in_.value = i
        dut._log.info(f"Loading operand A byte {i}")
        assert dut.state_out.value.integer == i + 1, "Incorrect state, should be loading operand A"
        assert dut.done.value == 0
        await RisingEdge(dut.clk)
        await ReadWrite()

    # Step 3: Feed operand B (4 bytes)
    for i in range(4):
        dut.in_.value = 10 + i
        dut._log.info(f"Loading operand B byte {i}")
        assert dut.state_out.value.integer == i + 5, "Incorrect state, should be loading operand B"
        assert dut.done.value == 0
        await RisingEdge(dut.clk)
        await ReadWrite()

    # Now in EXECUTE state
    assert dut.state_out.value.integer == 9, "Incorrect state, should be calculating"
    assert dut.done.value == 0

    await RisingEdge(dut.clk)
    await ReadWrite()

    # Step 5: Read all 4 output bytes
    for i in range(4):
        assert dut.state_out.value.integer == i + 10, "Incorrect state, should be outputting"
        assert dut.done.value == 1, "Done should be high when outputting result"

        # Log output byte
        dut._log.info(f"Result byte {i}: {dut.out.value.integer:02x}")

        await RisingEdge(dut.clk)
        await ReadWrite()

    assert dut.state_out.value == 0, "FSM should return to IDLE after output phase"
    assert dut.done.value == 0, "Done should be low after returning to IDLE"

    # Confirm still in IDLE if we don't set start to 1
    await RisingEdge(dut.clk)
    await ReadWrite()
    assert dut.state_out.value == 0, "FSM should remain in IDLE until start signal"
    assert dut.done.value == 0, "Done should be deasserted after returning to IDLE"
