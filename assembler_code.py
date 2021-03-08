# Assembler which converts all 37 rv32I instructons in hex and binary machine code
class InstructionTypes:

    branch_dict = {
            "beq": 0,
            "bne": 1,
            "blt": 4,
            "bge": 5,
            "bltu": 6,
            "bgeu": 7
            }

    load_dict = {
            "lb": 0,
            "lh": 1,
            "lw": 2,
            "lbu": 4,
            "lhu": 5
            }

    store_dict = {
            "sb": 0,
            "sh": 1,
            "sw": 2
            }

    arith_imm_dict = {
            "addi": 0,
            "slti": 2,
            "sltiu": 3,
            "xori": 4,
            "ori": 6,
            "andi": 7,
            "slli": 1,
            "srli": 5,
            "srai": 5
            }

    arith_dict = {
            "add": 0,
            "sub": 0,
            "slt": 2,
            "sltu": 3,
            "xor": 4,
            "or": 6,
            "and": 7,
            "sll": 1,
            "srl": 5,
            "sra": 5
            }





    def j_type(self, opcode, op, tokens):
        # JAL, JALR instructions
        rd = tokens[0] << 7

        if op == "jalr":
            if tokens[2] > 2047 or tokens[2] < -2048:
                return 0

            rs1 = tokens[1] << 15
            imm = (tokens[2] & 0xFFF) << 20
            return 0 | opcode | rd | rs1 | imm

        if tokens[1] > 524287 or tokens[1] < -524288:
            return 0

        imm = tokens[1]
        imm20 = ((imm >> 19) & 1) << 31
        imm10to1 = (imm & 0x3FF) << 21
        imm11 = ((imm >> 10) & 0x1) << 20
        imm19to12 = ((imm >> 11) & 0xFF) << 12
        return 0 | opcode | rd | imm19to12 | imm11 | imm10to1 | imm20


    def u_type(self, opcode, op, tokens):
        # LUI, AUIPC instructions
        if tokens[1] > 1048575 or tokens[1] < -1048576:
            return 0

        rd = tokens[0] << 7
        imm = tokens[1] << 12
        return 0 | opcode | rd | imm


    def b_type(self, opcode, op, tokens):
        # Branch instructions
        if tokens[2] > 511 or tokens[2] < -512:
            return 0

        funct3 = self.branch_dict[op] << 12
        rs1 = tokens[0] << 15
        rs2 = tokens[1] << 20
        imm = tokens[2]
        imm12 = (imm >> 11) << 31
        imm11 = ((imm >> 10) & 0x1) << 7
        imm10to5 = ((imm >> 4) & 0x3F) << 25
        imm4to1 = (imm & 0xF) << 8

        instr = 0 | opcode | imm11 | imm4to1 | funct3 | rs1 | rs2 | imm10to5 | imm12
        return instr


    def i_type(self, opcode, op, tokens):
        # Arith-Immediate instructions
        if tokens[2] > 511 or tokens[2] < -512:
            return 0

        funct3 = self.arith_imm_dict[op] << 12

        if op != "srai":
            funct7 = 0
        else:
            funct7 = 1 << 30

        rd = tokens[0] << 7
        rs1 = tokens[1] << 15
        imm = tokens[2] << 20
        instr = 0 | opcode | rd | funct3 | rs1 | imm

        if op in ["slli", "srli", "srai"]:
            instr = instr | funct7

        return instr


    def l_type(self, opcode, op, tokens):
        # Load instruction
        funct3 = self.load_dict[op] << 12

        rd = tokens[0] << 7
        rs1 = tokens[1] << 15
        imm = tokens[2] << 20
        instr = 0 | opcode | rd | funct3 | rs1 | imm

        return instr


    def s_type(self, opcode, op, tokens):
        # Store instructions
        funct3 = self.store_dict[op] << 12
        rs1 = tokens[0] << 15
        rs2 = tokens[1] << 20
        imm11to5 = (tokens[2] >> 5) << 25
        imm4to0 = (tokens[2] & 0x1F) << 7

        instr = 0 | opcode | imm4to0 | funct3 | rs1 | rs2 | imm11to5

        return instr


    def r_type(self, opcode, op, tokens):
        # Register instructions
        funct3 = self.arith_dict[op] << 12

        if op != "sub" and op != "sra":
            funct7 = 0
        else:
            funct7 = 1 << 30

        rd = tokens[0] << 7
        rs1 = tokens[1] << 15
        rs2 = tokens[2] << 20

        instr = 0 |funct7 | rs2 | rs1 | funct3 | rd | opcode

        return instr

class Assembler:   #instrctoins along with their opcodes

    instructions = {

        "add": [0b0110011, "r"],
        "sub": [0b0110011, "r"],
        "sll": [0b0110011, "r"],
        "slt": [0b0110011, "r"],
        "sltu": [0b0110011, "r"],
        "xor": [0b0110011, "r"],
        "srl": [0b0110011, "r"],
        "sra": [0b0110011, "r"],
        "or": [0b0110011, "r"],
        "and": [0b0110011, "r"],
        "addi": [0b0010011, "i"],
        "slti": [0b0010011, "i"],
        "sltiu": [0b0010011, "i"],
        "xori": [0b0010011, "i"],
        "ori": [0b0010011, "i"],
        "andi": [0b0010011, "i"],
        "slli": [0b0010011, "i"],
        "srli": [0b0010011, "i"],
        "lb": [0b0000011, "l"],
        "lh": [0b0000011, "l"],
        "lw": [0b0000011, "l"],
        "lbu": [0b0000011, "l"],
        "lhu": [0b0000011, "l"],
        "sb": [0b0100011, "s"],
        "sh": [0b0100011, "s"],
        "sw": [0b0100011, "s"],
        "lui": [0b0110111, "u"],
        "auipc": [0b0010111, "u"],
        "beq": [0b1100011, "b"],
        "bne": [0b1100011, "b"],
        "blt": [0b1100011, "b"],
        "bge": [0b1100011, "b"],
        "bltu": [0b1100011, "b"],
        "bgeu": [0b1100011, "b"],
        "jal": [0b1101111, "j"],
        "jalr": [0b1100111, "j"],

    }

    registers = {
            "zero": 0,
            "ra": 1,
            "sp": 2,
            "gp": 3,
            "tp": 4,
            "t0": 5,
            "t1": 6,
            "t2": 7,
            "s0": 8,
            "s1": 9,
            "a0": 10,
            "a1": 11,
            "a2": 12,
            "a3": 13,
            "a4": 14,
            "a5": 15,
            "a6": 16,
            "a7": 17,
            "s2": 18,
            "s3": 19,
            "s4": 20,
            "s5": 21,
            "s6": 22,
            "s7": 23,
            "s8": 24,
            "s9": 25,
            "s10": 26,
            "s11": 27,
            "t3": 28,
            "t4": 29,
            "t5": 30,
            "t6": 31
            }

    types = InstructionTypes()

    def convert(self, instr):
        types = self.types
        registers = self.registers
        instructions = self.instructions

        tokens = instr.lstrip().split(None, 1)
        tokens[1] = tokens[1].replace(" ", "").split(",")
        tokens_temp = []

#        print(tokens)
#        print(tokens[1])

        for token in tokens[1]:

            if token in registers:
                tokens_temp.append(registers[token])
            elif token[0] == "x":
                if len(token) == 2:
                    tokens_temp.append(int(token[1]))
                else:
                    tokens_temp.append(int(token[1:3]))
            elif self.is_dig(token):
                tokens_temp.append(int(token))
            else:
                print("Unexpected token")
                return 0

        tokens[1] = tokens_temp

        # Convert instruction to opcode
        op = tokens[0]
        opcode, instr_type = instructions[tokens[0]]
        args = tokens[1]
        bin_instr = 0


        if instr_type == "j":
            bin_instr = types.j_type(opcode, op, args)
        elif instr_type == "u":
            bin_instr = types.u_type(opcode, op, args)
        elif instr_type == "b":
            bin_instr = types.b_type(opcode, op, args)
        elif instr_type == "l":
            bin_instr = types.l_type(opcode, op, args)
        elif instr_type == "i":
            bin_instr = types.i_type(opcode, op, args)
        elif instr_type == "s":
            bin_instr = types.s_type(opcode, op, args)
        elif instr_type == "r":
            bin_instr = types.r_type(opcode, op, args)
        elif instr_type == "f":
            bin_instr = types.f_type(opcode, op, args)
        elif instr_type == "c":
            bin_instr = types.c_type(opcode, op, args)

        if bin_instr == 0:
            print("Error: Can't convert instruction: " + instr)
            return 0
        else:
            return bin_instr

    def is_dig(self, num_string):
        try:
            int(num_string)
            return True
        except ValueError:
            return False

def main():
    asm = Assembler()

    r_list = [
            "add x3, x5, x7",
            "sub x10, x11, x12",
            "sll x10, x11, x12",
            "slt x10, x11, x12",
            "sltu x10, x11, x12",
            "xor x10, x11, x12",
            "srl x10, x11, x12",
            "sra x10, x11, x12",
            "or x10, x11, x12",
            "and x10, x11, x12" ]

    j_list = [
            "jal ra, 524287",
            "jal ra, 339064",
            "jal ra, -524288",
            "jal ra, -524289",
            "jalr ra, a0, 2047",
            "jalr ra, a0, 2048",
            "jalr ra, a0, -2048",
            "jalr ra, a0, -2049"
            ]

    b_list = [
            "beq a0, a1, 4",
            "bne a0, a1, 4",
            "blt a0, a1, 4",
            "bge a0, a1, 4",
            "bltu a0, a1, 4",
            "bgeu a0, a1, 4"
            ]

    l_list = [
            "lb a0, a1, 4",
            "lh a0, a1, 4",
            "lw a0, a1, 4",
            "lbu a0, a1, 4",
            "lhu a0, a1, 4"
            ]

    s_list = [
            "sb a0, a1, 2201",
            "sh a0, a1, 2201",
            "sw a0, a1, 2201"
            ]

    i_list = [
            "addi x10, x11, 29",
            "slli x10, x11, 29",
            "slti x10, x11, 29",
            "sltiu x10, x11, 29",
            "xori x10, x11, 29",
            "srli x10, x11, 29",
            "ori x10, x11, 29",
            "andi x10, x11, 29" ]

    for instr in r_list:
        print(instr)
        print(hex(asm.convert(instr)))    #hexa decimal
        print(bin(asm.convert(instr)))    #binary conversion
    for instr in b_list:
        print(instr)
        print(hex(asm.convert(instr)))
        print(bin(asm.convert(instr)))
    for instr in i_list:
        print(instr)
        print(hex(asm.convert(instr)))
        print(bin(asm.convert(instr)))
    for instr in s_list:
        print(instr)
        print(bin(asm.convert(instr)))
    for instr in l_list:
        print(instr)
        print(bin(asm.convert(instr)))
if __name__ == "__main__":
    main()
