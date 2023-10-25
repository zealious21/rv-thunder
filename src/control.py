from amaranth import *

class control(Elaboratable):
    def __init__(self):

        self.instr = Signal(32)  # Input Instruction
        self.funct3 = Signal(3) # Function 3 
        self.funct7 = Signal() # Function 7
        self.rs1 = Signal(5) # Source Register 1
        self.rs2 = Signal(5) # Source Register 2
        self.rd = Signal(5) # Destination Register
        self.op = Signal(7) # Opcode
        self.we = Signal() # Register write enable (It will be 1 for R and I type and it is 0 for S type)
        self.ld_wd = Signal() #Load
        self.aluop = Signal(4) #ALU Operation
        self.sw = Signal() # Store Word (It will be 1 only if store instruction occur )
        self.imm = Signal(32) #Immediate
        self.iimm = Signal(12) # I type immediate
        self.simm = Signal(12) # S-type full immediate
        self.simm1 = Signal(5) # Sub1 immediate of S type
        self.simm2 = Signal(7) # Sub2 immediate of S type
        self.op_b_sel = Signal() # Operand B select bit for mux (Useful when there is an immediate)

#==========================< Instr Decode >===========================
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.op.eq (self.instr[0:]), # op is of 7 bits so (0 to 6)
            self.rd.eq (self.instr[7:]), # rd is of 5 bits so (7 to 11)
            self.funct3.eq (self.instr[12:]), #funct3 is of 3 bits so (12 to 14)
            self.rs1.eq (self.instr[15:]), # rs1 is of 5 bits so (15 to 19)
            self.rs2.eq (self.instr[20:]), # rs2 is of 5 bits so (20 to 24)
            self.funct7.eq (self.instr[30]), # funct3 is of 1 bit (30th bit)

#====================================Immediate for I type Instruction=========================== 
            self.iimm.eq (self.instr[20:]), # iimm is of 12 bits so (20 to 31)
#====================================Immediate for S type Instruction===========================
            self.simm1.eq (self.instr[7:]), # simm1 is of 5 bits so (7 to 11)
            self.simm2.eq (self.instr[25:]), # simm2 is of 7 bits so (25 to 31)
            self.simm.eq (Cat(self.simm1, self.simm2)), # simm is of 12 bits , make simm by concatenating both simm1 and simm2

            self.aluop.eq (Cat(self.funct3, self.funct7))
            ] # aluop is of 4 bits, make aluop by concatenating both funct3 and funct7

#=====================================< R-Type 33 >=====================================
        with m.Switch(self.op):
            with m.Case(0b0110011): # opcode of R-Type

                m.d.comb += [
                    self.we.eq(1),
                    self.op_b_sel.eq(0),
                    self.sw.eq(0)
                    ]

#=====================================< I-Type 13 >=====================================
            with m.Case(0b0010011): # opcode of I-Type
                m.d.comb += self.imm[0:12].eq(self.iimm) # put 12 bit iimm in first 12 bits of imm
                with m.If (self.imm[12] == 1): #check for sign extension, if it's 1 then convert (13 to 32) bits of imm to 1 otherwise 0
                    m.d.comb += self.imm[13:32].eq(1)
                with m.Else ():
                    m.d.comb += self.imm[13:32].eq(0)

                m.d.comb += [
                    self.we.eq(1),
                    self.op_b_sel.eq(1),
                    self.sw.eq(0)
                    ]

#=====================================< S-Type 23 >=====================================
            with m.Case(0b0100011): # opcode of S-Type
                m.d.comb += self.imm[0:12].eq(self.simm) #put 12 bit simm in first 12 bits of imm
                with m.If (self.imm[12] == 1):
                    m.d.comb += self.imm[13:32].eq(1)
                with m.Else ():
                    m.d.comb += self.imm[13:32].eq(0)

                m.d.comb += [
                    self.we.eq(0),
                    self.aluop.eq(0b0000),
                    self.op_b_sel.eq(1),
                    self.sw.eq(1)
                    ]
                
#=================================ld_wd========================================
            with m.Case(0b0000011): # opcode of Load Instruction
                m.d.comb += self.imm[0:12].eq(self.iimm)
                with m.If (self.imm[12] == 1):
                    m.d.comb += self.imm[13:32].eq(1)
                with m.Else ():
                    m.d.comb += self.imm[13:32].eq(0)

                m.d.comb += [
                    self.ld_wd.eq(1),
                    self.aluop.eq(0b0000),
                    self.op_b_sel.eq(1),
                    self.we.eq(1)
                    ]  

        return m

