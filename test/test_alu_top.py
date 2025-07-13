import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock


@cocotb.test()
async def test_alu_fsm_sequence(dut):
    """Test the full FSM sequence of alu_top.v"""

    # Start a 10ns period clock on dut.clk
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize all inputs
    dut.in_.value = 0
    dut.opcode.value = 0  # 0 = add
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

    # Step 1: Trigger start in IDLE
    assert dut.state_out.value == 0, "FSM should be in IDLE before start"
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0  # One-cycle pulse
    await RisingEdge(dut.clk)

    assert dut.state_out.value == 1, "FSM should transition to LOAD_A_0"

    # Step 2: Feed operand A (4 bytes)
    for i in range(4):
        dut.in_.value = i
        await RisingEdge(dut.clk)
        dut._log.info(f"Loaded operand A byte {i}")

    # Step 3: Feed operand B (4 bytes)
    for i in range(4):
        dut.in_.value = 10 + i
        await RisingEdge(dut.clk)
        dut._log.info(f"Loaded operand B byte {i}")

    # Step 4: Wait for EXECUTE
    while int(dut.state_out.value) != 9:
        await RisingEdge(dut.clk)

    dut._log.info("FSM entered EXECUTE state")
    await RisingEdge(dut.clk)  # Wait one cycle (holding EXECUTE)

    # Step 5: Wait for DONE_WAIT and assert done
    while int(dut.state_out.value) != 10:
        await RisingEdge(dut.clk)

    await RisingEdge(dut.clk)  # Wait for outputs to update

    assert dut.done.value == 1, "Done should be asserted in DONE_WAIT"
    dut._log.info("FSM entered DONE_WAIT and done asserted")

    # Step 6: Wait for OUTPUT_0 state and read first byte
    while int(dut.state_out.value) != 11:
        await RisingEdge(dut.clk)

    dut._log.info(f"Output byte 0: {dut.out.value.integer:02x}")

    # Step 7: Read remaining output bytes
    for i in range(1, 4):
        await RisingEdge(dut.clk)
        dut._log.info(f"Output byte {i}: {dut.out.value.integer:02x}")

    # Step 8: FSM should return to IDLE after OUTPUT_3
    while int(dut.state_out.value) != 0:
        await RisingEdge(dut.clk)

    dut._log.info("FSM returned to IDLE after output")
