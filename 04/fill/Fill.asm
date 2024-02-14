// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//// Replace this comment with your code.

(RESET)
@i
M=0
@color


(LOOP)
@color
M=0
@KBD
D=M
@PAINT
D;JEQ
@color
M=-1

(PAINT)
@SCREEN
D=A
@i
D=D+M
@R0
M=D 
@color
D=M
@R0
A=M
M=D

@i
M=M+1

@8192
D=A
@i
D=D-M
@RESET
D;JEQ

@LOOP
0;JMP


