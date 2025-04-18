@ ISW3_V0

@ a = a0 ^ a1 ^ a2, b = b0 ^ b1 ^ b2, c = c0 ^ c1 ^ c1, a * b = c, random numbers: rnd0, rnd1, rnd2

@ c0 = (a0*b0)^rnd0^rnd1
@ c1 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1)^rnd2
@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 

@  ^: xor; +: arithmathic addition; x & y: and operation; *: Galois field multiplication; &x: the address of x


.syntax unified
.text
.thumb  
.extern table       @ table is used for GFMULT (ai*bj multiplications)



.global Isw_3
.func Isw_3
Isw_3:

push  {lr}
push  {r4-r7}
mov   r4, r8
mov   r5, r9
mov   r6, r10
mov   r7, r11
push  {r4-r7}

// r0 = &a, r1 = &b, r2 = &rnd, r3 = &c

// Saving r3 (the address of the output)
mov  r8, r3        @r8 = &c

// Saving r0 (the address of the input a)
mov  r9, r0        @ r9 = &a

// Saving r1 (the address of the input b)
mov  r10, r1       @ r10 = &b

ldr  r3, =table    @ r3 = &table, The address of the "table", for ai*bj multiplications
// Reducing the use of LDR instruction: ldr rx,=table @ rx = &table; --> mov rx, r11 
mov  r11, r3       @ r11 = &table


# Start trigger ###############################
ldr  r4, =0xE0000004
movs r5, #1
str r5, [r4, #0]
###############################################
nop
nop


@@@@@ Loading arguments @@@@@@@@@@@@
ldrb r4, [r0, #0]  @ r4 = a0; r0 = &a, r1 = &b, r2 = &rnd, r3 = &table
ldrb r5, [r1, #0]  @ r5 = b0; r0 = &a, r1 = &b, r2 = &rnd, r3 = &table
ldrb r6, [r0, #4]  @ r6 = a1; r0 = &a, r1 = &b, r2 = &rnd, r3 = &table
ldrb r7, [r1, #4]  @ r7 = b1; r0 = &a, r1 = &b, r2 = &rnd, r3 = &table

@@@@@@@@@ Computing: ai*bi
@@@@ r0 = &a, r1 = &b, r2 = &rnd, r3 = &table
@@@@ r4 = a0, r5 = b0, r6 = a1, r7 = b1, 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a0*b0

ldrb r0, [r3, r4]   @ r0=table[a0]=loga0
ldrb r1, [r3, r5]   @ r1=table[b0]=logb0

adds r0, r1         @ r0=table[a0]+table[b0]=loga0+logb0

@@@@ Get the antilog:table[table[a0]+table[b0]+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r1, #250       @ r1 = 250, 256 is not possible, so it is split: 250 + 6
adds r1, #6         @ r1 = 256
adds r0, r1         @ r0 = table[a0]+table[b0]+256=loga0+logb0+256

ldrb r1, [r3, r0]   @ r1 =table[loga0+logb0+256]=exp(loga0+logb0)

# @@@@ Checking if a0 = 0 or b0 = 0, return 0; without conditional branch
negs r0, r4         @ r0 = -a0 hex(256-dec(a0)) = -a0

@@@ a0 in r4 is not needed any more, using r4
# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32        @ r4 = 32
asrs r0, r4         @ r0 = -a0>>32

ands r5, r0         @ r5=b0&(-a0>>32)
negs r5, r5         @ r5 = -(b0&(-a0>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r5, r4         @ r5 =-(b0&(-a0>>32))>>32

ands r5, r1         @ r5 = exp(loga0+logb0)&(-(b0&(-a0>>32))>>32)=(a0*b0)


@@@@ r0 = -a0 >> 32, r1 = exp(loga0+logb0), r2 = &rnd, r3 = &table
@@@@ r4 = #32, r5 = (a0*b0), r6 = a1, r7 = b1, 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a1*b1

ldrb r0, [r3, r6]   @ r0 =table[a1]=loga1
ldrb r1, [r3, r7]   @ r1 =table[b1]=logb1

adds r0, r1         @ r0 =table[a1]+table[b1]=loga1+logb1

@@@@ Get the antilog: table[loga1+logb1+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r1, #250       @ r1 = 250, 256 is not possible, so it is split: 250 + 6
adds r1, #6         @ r1 = 256
adds r0, r1         @ r0 = loga1+logb1+256

ldrb r1, [r3, r0]   @ r1 =table[loga1+logb1+256]=exp(loga1+logb1)

# @@@@ Checking if a1 = 0 or b1 = 0, return 0; without conditional branch
negs r0, r6         @ r0 = -a1

# @ asrs rd, <#imm> --> #imm: 0-31
movs r3, #32
asrs r0, r3         @ r0 = -a1>>32

ands r7, r0         @ r7 = b1&(-a1>>32)
negs r7, r7         @ r7 = -(b1&(-a1>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r7, r3         @ r7 = -(b1&(-a1>>32))>>32

ands r7, r1         @ r7 = exp(loga1+logb1) & (-(b1&(-a1>>32))>>32)=(a1*b1)

@@@@ r0 = -a1>>32, r1 = exp(loga1+logb1), r2 = &rnd, r3 = 32
@@@@ r4 = 32, r5 = (a0*b0), r6 = a1, r7 = (a1*b1), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a2*b2

mov  r0, r9         @ r0 = &a
mov  r1, r10        @ r1 = &b
mov  r4, r11        @ r4 = &table

ldrb r6, [r0, #8]   @ r6 = a2
ldrb r3, [r1, #8]   @ r3 = b2

ldrb r0, [r4, r6]   @ r0 =table[a2]=loga2
ldrb r1, [r4, r3]   @ r1 =table[b2]=logb2

adds r0, r1         @ r0 =table[a2]+table[b2]=loga2+logb2

@@@@ Get the antilog: table[loga2+logb2+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r1, #250       @ r1 = 250, 256 is not possible, so it is split: 250 + 6
adds r1, #6         @ r1 = 256
adds r0, r1         @ r0 = loga2+logb2+256

ldrb r1, [r4, r0]   @ r1 =table[loga2+logb2+256]=exp(loga2+logb2)

# @@@@ Checking if a2 = 0 or b2 = 0, return 0; without conditional branch
negs r0, r6         @ r0 = -a2

# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32
asrs r0, r4         @ r0 = -a2>>32

ands r3, r0         @ r3 = b2&(-a2>>32)
negs r3, r3         @ r3 = -(b2&(-a2>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r3, r4         @ r3 = -(b2&(-a2>>32))>>32

ands r3, r1         @ r3 = exp(loga2+logb2)&(-(b2&(-a2>>32))>>32)=(a2*b2)

mov  r4, r8         @ r4 = &c
strb r3, [r4, #8]   @ Storing (a2*b2) in c2, r3 = (a2*b2)

@@@@@@@@@ Computing: ci
@@@@ r0 = -a2>>32, r1 = exp(loga2+logb2), r2 = &rnd, r3 = (a2*b2),
@@@@ r4 = 32, r5 = (a0*b0), r6 = a2, r7 = (a1*b1), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c0 = (a0*b0)^rnd0^rnd1

ldrb r4, [r2, #0]   @ r4 = rnd0
ldrb r1, [r2, #4]   @ r1 = rnd1
eors r5, r4         @ r5 = (a0*b0)^rnd0
eors r1, r5         @ r1 = (a0*b0)^rnd0^rnd1=c0

mov  r0, r8         @ r0 = &c
strb r1, [r0, #0]   @ Storing c0, r1 =(a0*b0)^rnd0^rnd1=c0

@@@@ r0 = &c, r1 = c0, r2 = &rnd, r3 = (a2*b2),
@@@@ r4 = rnd0, r5 = (a0*b0)^rnd0, r6 = a2, r7 = (a1*b1), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c1 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1)^rnd2
@@@@ a0*b1

mov  r6, r9         @ r6 = &a
mov  r1, r10        @ r1 = &b
mov  r3, r11        @ r3 = &table

ldrb r5, [r6, #0]   @ r5 = a0
ldrb r0, [r1, #4]   @ r0 = b1

ldrb r6, [r3, r5]   @ r6 = table[a0]=loga0
ldrb r1, [r3, r0]   @ r1 = table[b1]=logb1

adds r6, r1         @ r6 =table[a0]+table[b1]=loga0+logb1

@@@@ Get the antilog: table[loga0+logb1+256]:
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r1, #250       @ r1 = 250, 256 is not possible, so it is split: 250 + 6
adds r1, #6         @ r1 = 256
adds r6, r1         @ r6 = loga0+logb1 + 256

ldrb r1, [r3, r6]   @ r1 = table[loga0+logb1+256]=exp(loga0+logb1)

# @@@@ Checking if a0 = 0 or b1 = 0, return 0; without conditional branch
negs r6, r5         @ r6 = -a0

# @ asrs rd, <#imm> --> #imm: 0-31
movs r3, #32
asrs r6, r3         @ r6 = -a0>>32

ands r0, r6         @ r0 =b1&(-a0>>32)
negs r0, r0         @ r0 = -(b1&(-a0>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r0, r3         @ r0 = -(b1&(-a0>>32))>>32

ands r0, r1         @ r0 = exp(loga0+logb1)&(-(b1&(-a0>>32))>>32)=(a0*b1)

eors r4, r0   @ r4 = (rnd0^(a0*b1))

@@@@ r0 = (a0*b1), r1 = exp(loga0+logb1), r2 = &rnd, r3 = #32
@@@@ r4 = (rnd0^(a0*b1)), r5 = a0, r6 = a0 >> 32, r7 = (a1*b1), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c1 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1)^rnd2
@@@@ a1*b0

mov  r0, r9         @ r0 = &a
mov  r5, r10        @ r5 = &b
mov  r6, r11        @ r6 = &table

ldrb r3, [r0, #4]   @ r3 = a1
ldrb r1, [r5, #0]   @ r1 = b0

ldrb r0, [r6, r3]   @ r0 = table[a1]=loga1
ldrb r5, [r6, r1]   @ r5 = table[b0]=logb0

adds r0, r5         @ r0 =table[a1]+table[b0]=loga1+logb0

@@@@ Get the antilog: table[loga1+logb0+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r5, #250       @ r5 = 250, 256 is not possible, so it is split: 250 + 6
adds r5, #6         @ r5 = 256
adds r0, r5         @ r0 =loga1+logb0+256

ldrb r5, [r6, r0]   @ r5 =table[loga1+logb0+256]=exp(loga1+logb0)

# @@@@ Checking if a1 = 0 or b0 = 0, return 0; without conditional branch
negs r0, r3         @ r0 = -a1

# @ asrs rd, <#imm> --> #imm: 0-31
movs r6, #32
asrs r0, r6         @ r0 = -a1>>32

ands r1, r0         @ r1 = b0&(-a1>>32)
negs r1, r1         @ r1 = -(b0&(-a1>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r1, r6         @ r1 = -(b0&(-a1>>32))>>32

ands r1, r5         @ r1 = exp(loga1+logb0)&(-(b0&(-a1>>32))>>32)=(a1*b0)

@@@@ r0 = -a1>>32, r1 = (a1*b0), r2 = &rnd, r3 = a1
@@@@ r4 = (rnd0^(a0*b1)), r5 = exp(loga1+logb0), r6 = 32 , r7 = (a1*b1), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c1 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1)^rnd2

ldrb r0, [r2, #8]   @ r0 = rnd2
eors r1, r4         @ r1 = [(rnd0^(a0*b1))^(a1*b0)]
eors r7, r1         @ r7 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1)
eors r0, r7         @ r0 = c1 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1)^rnd2

mov  r6, r8

strb r0, [r6, #4]   @ Storing c1, r0 = c1

@@@@ r0 = c1, r1 = [(rnd0^(a0*b1))^(a1*b0)], r2 = &rnd, r3 = a1
@@@@ r4 = (rnd0^(a0*b1)), r5 = exp(loga1+logb0), r6 = 32 , r7 = [(rnd0^(a0*b1))^(a1*b0)]^(a1*b1), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@ mov  r4, r8         @ r4 = &c
@@@@ strb r3, [r4, #8]   @ r3 = (a2*b2)
@@@@ (a2 *b2) is in [&c + #8]
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 
@@@@ a0*b2

mov  r0, r9         @ r0 = &a
mov  r7, r10        @ r7 = &b
mov  r4, r11        @ r4 = &table

ldrb r6, [r0, #0]   @ r6 = a0
ldrb r1, [r2, #4]   @ r1 = rnd1
ldrb r5, [r7, #8]   @ r5 = b2

ldrb r0, [r4, r6]   @ r0 =table[a0]=loga0
ldrb r7, [r4, r5]   @ r7 =table[b2]=logb2

adds r0, r7         @ r0 =table[a0]+table[b2]=loga0+logb2

@@@@ Get the antilog: table[loga0+logb2+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r7, #250       @ r7 = 250, 256 is not possible, so it is split: 250 + 6
adds r7, #6         @ r7 = 256
adds r0, r7         @ r0 = loga0+logb2+256

ldrb r7, [r4, r0]   @ r7 = table[loga0+logb2+256]=exp(loga0+logb2)

# @@@@ Checking if a0 = 0 or b2 = 0, return 0; without conditional branch
negs r0, r6         @ r0 = -a0

# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32
asrs r0, r4         @ r0 = -a0>>32

ands r5, r0         @ r5 = b2&(-a0>>32)
negs r5, r5         @ r5 = -(b2&(-a0>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r5, r4         @ r5 = -(b2&(-a0>>32))>>32

ands r5, r7         @ r5 = exp(loga0+logb2) & (-(b2&(-a0>>32))>>32)=(a0*b2)

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 
eors r1, r5           @ r1 = (rnd1^(a0*b2))

@@@@ r0 = -a0 >> 32, r1 = (rnd1^(a0*b2)), r2 = &rnd, r3 = a1
@@@@ r4 = 32, r5 = (a0*b2), r6 = a0 , r7 = exp(loga0+logb2), 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 
@@@@ a2*b0

mov  r5, r9         @ r5 = &a
mov  r6, r10        @ r6 = &b
mov  r4, r11        @ r4 = &table

ldrb r7, [r5, #8]   @ r7 = a2
ldrb r0, [r6, #0]   @ r0 = b0

ldrb r5, [r4, r7]   @ r5 =table[a2]=loga2
ldrb r6, [r4, r0]   @ r6 =table[b0]=logb0

adds r5, r6         @ r5 =table[a2]+table[b0]=loga2+logb0

@@@@ Get the antilog: table[loga2+logb0+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r6, #250       @ r6 = 250, 256 is not possible, so it is split: 250 + 6
adds r6, #6         @ r6 = 256
adds r5, r6         @ r5 = loga2+logb0+256

ldrb r6, [r4, r5]   @ r6 =table[loga2+logb0+256]=exp(loga2+logb0)

# @@@@ Checking if a2 = 0 or b0 = 0, return 0; without conditional branch
negs r5, r7         @ r5 = -a2

# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32
asrs r5, r4         @ r5 = -a2>>32

ands r0, r5         @ r0 =b0&(-a2>>32)
negs r0, r0         @ r0 = -(b0&(-a2>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r0, r4         @ r0 = -(b0&(-a2>>32))>>32

ands r0, r6         @ r0 = exp(loga2+logb0)&(-(b0&(-a2>>32))>>32)=(a2*b0)

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 
eors r0, r1         @ r0 = [(rnd1^(a0*b2))^(a2*b0)]

@@@@ r0 = [(rnd1^(a0*b2))^(a2*b0)], r1 = (rnd1^(a0*b2)), r2 = &rnd, r3 = a1
@@@@ r4 = 32, r5 = -a2 >> 32, r6 =exp(loga2+logb0), r7 = a2, 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 
@@@@ a1*b2

mov  r5, r10        @ r5 = &b
mov  r4, r11        @ r4 = &table

ldrb r6, [r2, #8]   @ r6 = rnd2   @ From here r2 can be used
ldrb r1, [r5, #8]   @ r1 = b2

ldrb r2, [r4, r3]   @ r2 =table[a1]=loga1
ldrb r5, [r4, r1]   @ r5 =table[b2]=logb2

adds r2, r5         @ r2 =table[a1]+table[b2]=loga1+logb2

@@@@ Get the antilog: table[loga1+logb2+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r5, #250       @ r5 = 250, 256 is not possible, so it is split: 250 + 6
adds r5, #6         @ r5 = 256
adds r2, r5         @ r2 = loga1+logb2+256

ldrb r5, [r4, r2]   @ r5 =table[loga1+logb2+256]

# @@@@ Checking if a1 = 0 or b2 = 0, return 0; without conditional branch
negs r2, r3         @ r2 = -a1

# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32
asrs r2, r4         @ r2 = -a1>>32

ands r1, r2         @ r1 = b2&(-a1>>32)
negs r1, r1         @ r1 = -(b2&(-a1>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r1, r4         @ r1 = -(b2&(-a1>>32))>>32

ands r1, r5         @ r1 = exp(loga1+logb2)&(-(b2&(-a1>>32))>>32)=(a1*b2)
eors r6, r1         @ r6 = (rnd2^(a1*b2))

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ r0 = [(rnd1^(a0*b2))^(a2*b0)], r1 = (a1*b2), r2 = -a1 >> 32, r3 = a1
@@@@ r4 = 32, r5 = exp(loga1+logb2), r6 = (rnd2^(a1*b2)), r7 = a2, 
@@@@ r8 = &c, r9 = &a, r10 = &b, r11 = &table 
@@@@ mov  r4, r8         @ r4 = &c
@@@@ strb r3, [r4, #8]   @ r3 = (a2*b2)
@@@@ (a2 *b2) is in [&c + #8]
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 
@@@@ a2*b1

mov  r2, r8         @ r2 = &c  @ (a2 *b2) is in [&c + #8]
mov  r4, r11        @ r4 = &table
mov  r3, r10        @ r3 = &b

ldrb r5, [r2, #8]   @ r5 = (a2*b2)
ldrb r1, [r3, #4]   @ r1 = b1

ldrb r2, [r4, r7]   @ r2 = table[a2]=loga2
ldrb r3, [r4, r1]   @ r3 = table[b1]=logb1

adds r2, r3         @ r2 =table[a2]+table[b1]=loga2+logb1

@@@@ Get the antilog: table[loga2+logb1+256]
# @ adds rd, <#imm> --> #imm: 3 bits, 0-7
# @ movs rd, <#imm> --> #imm: 0-255
movs r3, #250       @ r3 = 250, 256 is not possible, so it is split: 250 + 6
adds r3, #6         @ r3 = 256
adds r2, r3         @ r2 =loga2+logb1+256

ldrb r3, [r4, r2]   @ r3 =table[loga2+logb1+256]

# @@@@ Checking if a2 = 0 or b1 = 0, return 0; without conditional branch
negs r2, r7         @ r2 = -a2

# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32
asrs r2, r4         @ r2 = -a2>>32

ands r1, r2         @ r1 =b1&(-a2>>32)
negs r1, r1         @ r1 =-(b1&(-a2>>32))

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r1, r4         @ r1 = -(b1&(-a2>>32))>>32

ands r1, r3         @ r1 = exp(loga2+logb1)&(-(b1&(-a2>>32))>>32)=(a2*b1)

@@@@ c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2) 

mov  r4, r8         @ r4 = &c
eors r6, r1         @ r6 = [(rnd2^(a1*b2))^(a2*b1)]
eors r0, r6         @ r0 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]
eors r5, r0         @ r5 = c2 = [(rnd1^(a0*b2))^(a2*b0)]^[(rnd2^(a1*b2))^(a2*b1)]^(a2*b2)

strb r5, [r4, #8]   @ Storing c2, r5 = c2


nop
nop
# End trigger ###############################
ldr  r4, =0xE0000004
movs r5, #0
str r5, [r4, #0]
#############################################

pop  {r4-r7}
mov   r8, r4
mov   r9, r5
mov   r10, r6
mov   r11, r7
pop   {r4-r7}
pop  {pc}
.endfunc 

.end






