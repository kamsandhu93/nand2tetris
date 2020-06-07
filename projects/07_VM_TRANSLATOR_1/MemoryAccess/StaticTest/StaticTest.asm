// push constant 111
@111
D=A
@0
A=M
M=D
@0
M=M+1
// push constant 333
@333
D=A
@0
A=M
M=D
@0
M=M+1
// push constant 888
@888
D=A
@0
A=M
M=D
@0
M=M+1
// pop static 8
@0
A=M-1
D=M
@static.8
M=D
@0
M=M-1
// pop static 3
@0
A=M-1
D=M
@static.3
M=D
@0
M=M-1
// pop static 1
@0
A=M-1
D=M
@static.1
M=D
@0
M=M-1
// push static 3
@static.3
D=M
@0
A=M
M=D
@0
M=M+1
// push static 1
@static.1
D=M
@0
A=M
M=D
@0
M=M+1
// sub
@0
A=M-1
D=M
@0
A=M-1
A=A-1
M=M-D
@0
M=M-1
// push static 8
@static.8
D=M
@0
A=M
M=D
@0
M=M+1
// add
@0
A=M-1
D=M
@0
A=M-1
A=A-1
M=D+M
@0
M=M-1
