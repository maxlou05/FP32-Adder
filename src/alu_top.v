`default_nettype none

module alu_top (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] in,
    output reg  [7:0] out,

    input  wire       opcode,
    input  wire       start,
    output reg        done,
    output wire [3:0] state_out
);

    parameter IDLE        = 4'd0;
    parameter LOAD_A_0    = 4'd1;
    parameter LOAD_A_1    = 4'd2;
    parameter LOAD_A_2    = 4'd3;
    parameter LOAD_A_3    = 4'd4;
    parameter LOAD_B_0    = 4'd5;
    parameter LOAD_B_1    = 4'd6;
    parameter LOAD_B_2    = 4'd7;
    parameter LOAD_B_3    = 4'd8;
    parameter EXECUTE     = 4'd9;
    parameter DONE_WAIT   = 4'd10;
    parameter OUTPUT_0    = 4'd11;
    parameter OUTPUT_1    = 4'd12;
    parameter OUTPUT_2    = 4'd13;
    parameter OUTPUT_3    = 4'd14;

    reg [3:0]  state;
    reg [31:0] operand_a;
    reg [31:0] operand_b;
    reg [31:0] result;
    reg        execute_flag;

    assign state_out = state;

    wire sub = opcode;
    wire [31:0] addsub_result;

    fp_addsub u_addsub (
        .a      (operand_a),
        .b      (operand_b),
        .sub    (sub),
        .result (addsub_result)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= IDLE;
            operand_a     <= 32'd0;
            operand_b     <= 32'd0;
            result        <= 32'd0;
            out           <= 8'd0;
            done          <= 1'b0;
            execute_flag  <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    done         <= 1'b0;
                    execute_flag <= 1'b0;
                    if (start)
                        state <= LOAD_A_0;
                end

                LOAD_A_0: begin operand_a[7:0]    <= in; state <= LOAD_A_1; end
                LOAD_A_1: begin operand_a[15:8]   <= in; state <= LOAD_A_2; end
                LOAD_A_2: begin operand_a[23:16]  <= in; state <= LOAD_A_3; end
                LOAD_A_3: begin operand_a[31:24]  <= in; state <= LOAD_B_0; end

                LOAD_B_0: begin operand_b[7:0]    <= in; state <= LOAD_B_1; end
                LOAD_B_1: begin operand_b[15:8]   <= in; state <= LOAD_B_2; end
                LOAD_B_2: begin operand_b[23:16]  <= in; state <= LOAD_B_3; end
                LOAD_B_3: begin operand_b[31:24]  <= in; state <= EXECUTE;  end

                EXECUTE: begin
                    if (!execute_flag) begin
                        result        <= addsub_result;
                        execute_flag  <= 1'b1;
                        state         <= EXECUTE;  // Hold EXECUTE for 1 cycle
                    end else begin
                        execute_flag  <= 1'b0;
                        state         <= DONE_WAIT;
                    end
                end

                DONE_WAIT: begin
                    done  <= 1'b1;       // Signal result ready
                    state <= OUTPUT_0;   // Next cycle begins output
                end

                OUTPUT_0: begin
                    done  <= 1'b0;           // Drop done now
                    out   <= result[7:0];    // Output byte 0
                    state <= OUTPUT_1;
                end

                OUTPUT_1: begin
                    out   <= result[15:8];   // Output byte 1
                    state <= OUTPUT_2;
                end

                OUTPUT_2: begin
                    out   <= result[23:16];  // Output byte 2
                    state <= OUTPUT_3;
                end

                OUTPUT_3: begin
                    out   <= result[31:24];  // Output byte 3
                    state <= IDLE;           // Return to IDLE
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
