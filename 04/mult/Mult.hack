@R0
D=M
@LOOP
D;JGT       // R0 > 0 ?
@R0
M=-M        // R0 = -R0
@R1
M=-M        // R1 = -R1

@R2
M=0         // R2 = 0

(LOOP)
@R0
D=M
@STOP
D;JEQ       // R0 == 0 ?

@R1
D=M
@R2
M=M + D     // R2 = R2 + R1

@R0
M=M-1       // R0 = R0 - 1
@LOOP
0;JMP

(STOP)
@END
0;JMP

(END)
@END
0;JMP