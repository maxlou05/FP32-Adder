# Sample testbench for a Tiny Tapeout project

This is a sample testbench for a Tiny Tapeout project. It uses [cocotb](https://docs.cocotb.org/en/stable/) to drive the DUT and check the outputs.
See below to get started or for more information, check the [website](https://tinytapeout.com/hdl/testing/).

## Setting up

1. Edit [Makefile](Makefile) and modify `PROJECT_SOURCES` to point to your Verilog files.
2. Edit [tb.v](tb.v) and replace `tt_um_example` with your module name.
3. Make a Python virtual environment and do `pip install -r requirements.txt`
4. Get `iverilog`: `sudo apt-get update && sudo apt-get install iverilog`
5. (Optional) Get `gtkwave` to see the signals as waveforms: `sudo apt-get install gtkwave`

## How to run

To run the RTL simulation:

```sh
make -B
```

To run gatelevel simulation, first harden your project and copy `../runs/wokwi/results/final/verilog/gl/{your_module_name}.v` to `gate_level_netlist.v`.

This is in github actions. Go to the `Summary` page of github actions (top left, where you see the chip usage). Scroll down to the bottom until you see the `Artifacts` section and download `tt_submission`.
The `{your_module_name}.v` will be in there.

Then run:

```sh
export PDK_ROOT=./pdk  # Depending on where you execute this next line, it may be advised to use an absolute path. Replace '.' with this current directory
volare enable --pdk "sky130" "cd1748bb197f9b7af62a54507de6624e30363943"
GATES=yes make -B
```

## How to view the VCD file
A `.vcd` file will be generated after you run a test.

Using GTKWave
```sh
gtkwave tb.vcd tb.gtkw
```

Using Surfer
```sh
surfer tb.vcd
```
