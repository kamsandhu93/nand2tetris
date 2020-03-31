// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// LOOP
// IF keyboard = 0
// MAKE SCREEN WHITE
// LOOP OVER ALL ARRAYS SETTING TO WHITE \\
// BACK TO OUTTER LOOP

// MAKE ALL SCREEN BLACK
// BACK TO OUTER LOOP




(LOOP)
  @KBD
  D=M

  @IS_BLACK_LOOP
  D;JNE


(IS_WHITE_LOOP)
  // get start screen
  // set n which is max number of loops
  // set i which is loop itter
  // make addr black
  // add 1 to addr
  // check if i is bigger than n if so jump to loop

  @SCREEN
  D=A
  @addr
  M=D

  @8191
  D=A
  @n
  M=D
  @i
  M=1


(WHITE_LOOP)
  @addr
  A=M
  M=0 // Set memory at addr to white

  @addr
  M=M+1 // incr addr

  @i // check if i is bigger than n if so break loop
  D=M
  @n
  D=D-M
  @LOOP
  D;JGT

  @i
  M=M+1

  @WHITE_LOOP
  0;JMP

(IS_BLACK_LOOP)
  // get start screen
  // set n which is max number of loops
  // set i which is loop itter
  // make addr black
  // add 1 to addr
  // check if i is bigger than n if so jump to loop

  @SCREEN
  D=A
  @addr
  M=D

  @8191
  D=A
  @n
  M=D
  @i
  M=1


(BLACK_LOOP)
  @addr
  A=M
  M=-1 // Set memory at addr to black

  @addr
  M=M+1 // incr addr

  @i // check if i is bigger than n if so break loop
  D=M
  @n
  D=D-M
  @LOOP
  D;JGT

  @i
  M=M+1


  @BLACK_LOOP
  0;JMP
