// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)


// save r0 to sum variable
// save 2r to n variable
// save i = 0

// loop n times adding adding to sum

// exit loop

//set r2 to result


    @i
    M=1

    @sum
    M=0

    // make n number of loops = r1
    @R1
    D=M
    @n
    M=D

  (LOOP)
    @i
    D=M

    @n
    D=D-M

    @STOP
    D;JGT


    @sum
    D=M
    @R0
    D=D+M
    @sum
    M=D

    @i
    M=M+1

    @LOOP
    0;JMP


  (STOP)
    @sum
    D=M
    @R2
    M=D

  (END)
    @END
    0;JMP





