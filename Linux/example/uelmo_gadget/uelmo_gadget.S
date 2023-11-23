//An ISW-2 implementatoin by Nima Mahdion.
.syntax unified
.text
.thumb
.extern table       @ table is used for GFMULT (ai*bj multiplications)

.global Isw_2
.func Isw_2
Isw_2:

push  {lr}
push  {r4-r7}
mov   r4, r8
mov   r5, r9
mov   r6, r10
mov   r7, r11
push  {r4-r7}

//r0 = &a, r1 = &b, r2 = &rnd, r3 = &c

//Saving r3 (the address of the output)
mov  r8, r3        @r8 = &c

//Saving r0 (the address of the input a)
mov  r9, r0        @ r9 = &a

//Saving r1 (the address of the input b)
mov  r10, r1       @ r10 = &b
ldr  r3, =table    @ r3 = &taable, The address of the "table", for ai*bj multiplications

//Reducing the use of LDR instruction: ldr rx,=table @ rx = &table; --> mov rx, r11 
mov  r11, r3       @ r11 = &table


# Start trigger ###############################
ldr  r4, =0xE0000004
movs r5, #1
str r5, [r4, #0]
###############################################

nop
nop

@@@@ r0 = &a, r1 = &b, r2 = &rnd, r4 = &table
@@@@ r8 = &c, r9 = &table, r11 = 256
@@@@@ Loading arguments @@@@@@@@@@@@
ldrb r6, [r0, #0] @ r6 = a0; r0 = &a, r1 = &b, r2 = rnd
ldrb r5, [r1, #0] @ r5 = b0; r0 = &a, r1 = &b, r2 = rnd
ldrb r3, [r0, #4] @ r3 = a1; r0 = &a, r1 = &b, r2 = rnd
ldrb r7, [r1, #4] @ r7 = b1; r0 = &a, r1 = &b, r2 = rnd
ldrb r2, [r2, #0] @ r2 = rnd;r0 = &a, r1 = &b


@@@@@@@@@ Computing c0 = (a0 * b0) + rnd

@@@@ r0 = &a, r1 = &b, r2 = rnd, r4 = &table
@@@@ r3 = a1, r5 = b0, r6 = a0, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a0 * b0

ldrb r1, [r4, r5]   @ r1 = table[b0]
ldrb r0, [r4, r6]   @ r0 = table[a0]

adds r0, r1         @ r0 = s = table[a0] + table[b0]

@@@@ Get the antilog: s = table[s+256]: g + s
mov  r1, r11        @ r1 = 256

adds r0, r1         @ r0 = s + 256
ldrb r1, [r4, r0]   @ r1 = s = table[s+256]

# @@@@ Checking if a0 = 0 or b0 = 0, return 0; without conditional branch
negs r0, r6         @ r0 = -a0 hex(256-dec(a0))

# @ asrs rd, <#imm> --> #imm: 0-31
movs r4, #32        @ r4 = #32
asrs r0, r4         @ r0 = -a0 >> 32

ands r0, r5         @ r0 = tmp = b0 & (-a0 >> 32)
negs r0, r0         @ r0 = -tmp

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r0, r4         @ r0 = -tmp >> 32

ands r1, r0         @ r1 = s & (-tmp >> 32) = (a0 * b0)

@@@@ (a0 * b0) + rnd

mov  r4, r8         @ r4 = &c
eors r1, r2         @ r1 = c0 = (a0 * b0) + rnd
strb r1, [r4, #0]   @ Storing c0, r1 = c0

@@@@@@@@@ Computing c1 = [((a0 * b1) + rnd) + (a1 * b0)] + (a1 * b1)

@@@@ r0 = -tmp >> 32, r1 = c0, r2 = rnd, r4 = &c
@@@@ r3 = a1, r5 = b0, r6 = a0, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a0 * b1

mov  r1, r9         @ r1 = &table 
ldrb r0, [r1, r6]   @ r0 = table[a0]
ldrb r4, [r1, r7]   @ r4 = table[b1]

adds r0, r4         @ r0 = s = table[a0] + table[b1]

@@@@ Get the antilog: s = table[s+256]: g + s
mov  r4, r11        @ r4 = 256

adds r0, r4         @ r0 = s + 256

ldrb r4, [r1, r0]   @ r4 = s = table[s+256]

# @@@@ Checking if a0 = 0 or b1 = 0, return 0; without conditional branch
negs r0, r6         @ r0 = -a0 hex(256-dec(a0))

# @ asrs rd, <#imm> --> #imm: 0-31
@ a0 in r6 is not needed anymore, r6 can be used
movs r6, #32        @ r6 = #32
asrs r0, r6         @ r0 = -a0 >> 32

ands r0, r7         @ r0 = tmp = b1 & (-a0 >> 32)
negs r0, r0         @ r0 = -tmp

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r0, r6         @ r0 = -tmp >> 32

ands r0, r4         @ r0 = s & (-tmp >> 32) = (a0 * b1)

@@@@ (a0 * b1) + rnd

eors r2, r0         @ r2 = (a0 * b1) + rnd

@@@@ r0 = (a0 * b1), r1 =  &table, r2 = (a0 * b1) + rnd, r4 = table[s+256]
@@@@ r3 = a1, r5 = b0, r6 = 32, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a1 * b0

ldrb r0, [r1, r3]   @ r0 = table[a1]
ldrb r4, [r1, r5]   @ r4 = table[b0]

adds r0, r4         @ r0 = s = table[a1] + table[b0]

@@@@ Get the antilog: s = table[s+256]: g + s
mov  r4, r11        @ r4 = 256

adds r0, r4         @ r0 = s + 256

ldrb r4, [r1, r0]   @ r4 = s = table[s+256]

# @@@@ Checking if a1 = 0 or b0 = 0, return 0; without conditional branch
negs r0, r3         @ r0 = -a1 hex(256-dec(a1))

# @ asrs rd, <#imm> --> #imm: 0-31
# movs r6, #32        @ r6 = #32
asrs r0, r6         @ r0 = -a1 >> 32

ands r0, r5         @ r0 = tmp = b0 & (-a1 >> 32)
negs r0, r0         @ r0 = -tmp

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r0, r6         @ r0 = -tmp >> 32

ands r0, r4         @ r0 = s & (-tmp >> 32) = (a1 * b0)

@@@@ ((a0 * b1) + rnd) + (a1 * b0)

eors r0, r2         @ r0 = ((a0 * b1) + rnd) + (a1 * b0)

@@@@ r0 = ((a0 * b1) + rnd) + (a1 * b0), r1 = &table, r2 = ((a0 * b1) + rnd), r4 = table[s+256]
@@@@ r3 = a1, r5 = b0, r6 = 32, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@ a1 * b1

ldrb r5, [r1, r3]   @ r5 = table[a1]
ldrb r4, [r1, r7]   @ r4 = table[b1]

adds r5, r4         @ r5 = s = table[a1] + table[b1]

@@@@ Get the antilog: s = table[s+256]: g + s
mov  r2, r11        @ r2 = 256

adds r5, r2         @ r5 = s + 256

ldrb r4, [r1, r5]   @ r4 = s = table[s+256]

# @@@@ Checking if a1 = 0 or b1 = 0, return 0; without conditional branch
negs r5, r3         @ r5 = -a1 hex(256-dec(a1))

# @ asrs rd, <#imm> --> #imm: 0-31
# movs r6, #32        @ r6 = #32
asrs r5, r6         @ r5 = -a1 >> 32

ands r5, r7         @ r5 = tmp = b1 & (-a1 >> 32)
negs r5, r5         @ r5 = -tmp

# @ asrs rd, <#imm> --> #imm: 0-31
asrs r5, r6         @ r5 = -tmp >> 32

ands r4, r5         @ r4 = s & (-tmp >> 32) = (a1 * b1)

mov  r1, r8         @ r1 = &c

@@@@ c1
eors r4, r0         @ r4 =  [((a0 * b1) + rnd) + (a1 * b0)] + (a1 * b1)

strb r1, [r1, #4]   @ Clearing the write bus
strb r4, [r1, #4]   @ Storing c1, r4 = c1


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
