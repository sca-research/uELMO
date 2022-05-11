.syntax unified
  .text
  .thumb

  .extern table       @@@@ table is used for GFMULT (ai * bj multiplications)

@@@@ extern void Isw_1(uint8_t* inputa: addres: r0, uint8_t* inputb: address: r1, uint8_t* rnd: address: r2, uint8_t* output: address: r3);
@inputa: a0, a1, inputb: b0, b1, rnd: rnd, output: c: c0, c1
@@@@ extern void Isw_1(r0, r1, r2, r3);

@@@@ c0 = (a0 * b0) ^ rnd
@@@@ c1 = [((a0 * b1) ^ rnd) ^ (a1 * b0)] ^ (a1 * b1)



.global Isw_1
.func Isw_1
Isw_1:

  push  {lr}

  # This programm is written using Thumb-16 instructions.
  # In Thumb-16 registerlist in push/pop can not contain High registers.
  # As a result, instead of push/pop {r4-r11}, the following instructions are used.

  # about MOV and MOVS instructions in thumb-16:
  # MOVS: #imm to LOWreg, and LOWreg to LOWreg
  # MOV:any_reg to any_reg
  # For moving reg to reg we use MOV, for moving #imm to reg we use MOVS

  push  {r4-r7}
  mov   r4, r8
  mov   r5, r9
  mov   r6, r10
  mov   r7, r11
  push  {r4-r7}


@@@@@ r0 = &a, r1 = &b, r2 = &rnd, r3 = &c

/********************* Beginning of annotations *******************/
/***** annotations for uelmo start with @src or @dst ********/
 
@@@@@ Saving r3 (the address of the output)
  @src r3 , &c
  @dst r8 , &c
  mov  r8, r3        


@@@@ Saving the value 256 in r11. This decreases one cycle.
  # @ adds rd, <#imm> --> #imm: 3 bits, 0-7
  # @ movs rd, <#imm> --> #imm: 0-255
  @dst r4 , #250
  movs r4, #250      
  
  @dst r4 , #256
  adds r4, #6         
  
  // @src r4 , #256
  @dst r11 , #256 
  mov  r11, r4        

  @src =table , &table
  @dst r3 , &table
  ldr  r3, =table    @ r3 = &table, The address of the "table", for ai * bj multiplications
@@@@ Reducing the use of LDR instruction: ldr rx,=table @ rx = &table; --> mov rx, r11 
  mov  r9, r3        @ r9 = &table


nop
nop
nop
nop



@@@@ r0 = &a, r1 = &b, r2 = &rnd, r3 = &table
@@@@ r8 = &c, r9 = &table, r11 = 256
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@ Loading arguments @@@@@@@@@@@@
  @src r0 , &a
  @dst r6 , a0
  ldrb r6, [r0, #0]
  
  @src r2 , &rnd
  @dst r2 , rnd
  ldrb r2, [r2, #0]
  
  @src r1 , &b
  @dst r5 , b0
  ldrb r5, [r1, #0]
  
  @src r0 , &a
  @dst r4 , a1
  ldrb r4, [r0, #4]
  
  @src r1 , &b
  @dst r7 , b1
  ldrb r7, [r1, #4]


@@@@@@@@@ Computing c0 = (a0 * b0) ^ rnd

@@@@ r0 = &a, r1 = &b, r2 = rnd, r3 = &table
@@@@ r4 = a1, r5 = b0, r6 = a0, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@ a0 * b0

  @dst r0 , table[a0]
  ldrb r0, [r3, r6]   
  
  @dst r1 , table[0]
  ldrb r1, [r3, #0]   @ clearing the read bus, r1 = table[0]= 0 , ADD
  
  @dst r1 , table[b0]
  ldrb r1, [r3, r5] 

  @var v0 , table[a0] + table[b0]
  @dst r0 , v0
  adds r0, r1       

 
  @dst r1 , #256
  mov  r1, r11        

  @var v1 , v0 + 256
  @dst r0 , v1
  adds r0, r1        

##################

  @var v2 , table[v1]
  @dst r1, v1
  ldrb r1, [r3, r0]  

  # @@@@ Checking if a0 = 0 or b0 = 0, return 0; without conditional branch
  @var v3 , -a0
  @dst r0 , v3
  negs r0, r6    

  # @ asrs rd, <#imm> --> #imm: 0-31
  @dst r3 , #32
  movs r3, #32    
  
  @var v4 , v3 >> 32
  @dst r0 , v4
  asrs r0, r3    

  @var v5 , v4 & b0
  @dst r0 , v5
  ands r0, r5      
 
  @var v6 , -v5
  @dst r0 , v6
  negs r0, r0      

  # @ asrs rd, <#imm> --> #imm: 0-31
  @var v7 , v6 >> 32
  @dst r0 , v7
  asrs r0, r3     

  @var v8 , a0 * b0 
  @dst r1 , v8
  ands r1, r0      
  
  @@@@ (a0 * b0) ^ rnd

  @dst r3 , &c
  mov  r3, r8

  @var v9 , v8 ^ rnd
  @dst r1 , v9
  eors r1, r2        

  strb r1, [r3, #0] 


/********************* End of annotations *******************/

@@@@@@@@@ Computing c1 = [((a0 * b1) ^ rnd) ^ (a1 * b0)] ^ (a1 * b1)

@@@@ r0 = -tmp >> 32, r1 = c0, r2 = rnd, r3 = &c
@@@@ r4 = a1, r5 = b0, r6 = a0, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@ a0 * b1

  mov  r1, r9         @ r1 = &table 
  ldrb r0, [r1, r6]   @ r0 = table[a0]
  ldrb r3, [r1, #0]   @ clearing the read bus, r3 = table[0]= 0 , ADD
  ldrb r3, [r1, r7]   @ r3 = table[b1]

  adds r0, r3         @ r0 = s = table[a0] + table[b1]

  @@@@ Get the antilog: s = table[s+256]: g ^ s
  mov  r3, r11        @ r3 = 256

  adds r0, r3         @ r0 = s + 256

  ldrb r3, [r1, r0]   @ r3 = s = table[s+256]

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

  ands r0, r3         @ r0 = s & (-tmp >> 32) = (a0 * b1)
  
  @@@@ (a0 * b1) ^ rnd

  eors r2, r0         @ r2 = (a0 * b1) ^ rnd


@@@@ r0 = (a0 * b1), r1 =  &table, r2 = (a0 * b1) ^ rnd, r3 = table[s+256]
@@@@ r4 = a1, r5 = b0, r6 = 32, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@ a1 * b0

  ldrb r0, [r1, r4]   @ r0 = table[a1]
  ldrb r3, [r1, #0]   @ clearing the read bus, r3 = table[0]= 0 , ADD
  ldrb r3, [r1, r5]   @ r3 = table[b0]

  adds r0, r3         @ r0 = s = table[a1] + table[b0]

  @@@@ Get the antilog: s = table[s+256]: g ^ s
  mov  r3, r11        @ r3 = 256

  adds r0, r3         @ r0 = s + 256

  ldrb r3, [r1, r0]   @ r3 = s = table[s+256]

  # @@@@ Checking if a1 = 0 or b0 = 0, return 0; without conditional branch
  negs r0, r4         @ r0 = -a1 hex(256-dec(a1))

  # @ asrs rd, <#imm> --> #imm: 0-31
  # movs r6, #32        @ r6 = #32
  asrs r0, r6         @ r0 = -a1 >> 32

  ands r0, r5         @ r0 = tmp = b0 & (-a1 >> 32)
  negs r0, r0         @ r0 = -tmp

  # @ asrs rd, <#imm> --> #imm: 0-31
  asrs r0, r6         @ r0 = -tmp >> 32

  ands r0, r3         @ r0 = s & (-tmp >> 32) = (a1 * b0)
 

  @@@@ ((a0 * b1) ^ rnd) ^ (a1 * b0)

  eors r0, r2         @ r0 = ((a0 * b1) ^ rnd) ^ (a1 * b0)


@@@@ r0 = ((a0 * b1) ^ rnd) ^ (a1 * b0), r1 = &table, r2 = ((a0 * b1) ^ rnd), r3 = table[s+256]
@@@@ r4 = a1, r5 = b0, r6 = 32, r7 = b1, 
@@@@ r8 = &c, r9 = &table, r11 = 256 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@ a1 * b1

  ldrb r5, [r1, r4]   @ r5 = table[a1]
  ldrb r3, [r1, #0]   @ clearing the read bus, r3 = table[0]= 0 , ADD
  ldrb r3, [r1, r7]   @ r3 = table[b1]

  adds r5, r3         @ r5 = s = table[a1] + table[b1]

  @@@@ Get the antilog: s = table[s+256]: g ^ s
  mov  r2, r11        @ r2 = 256

  adds r5, r2         @ r5 = s + 256

  ldrb r3, [r1, r5]   @ r3 = s = table[s+256]

  # @@@@ Checking if a1 = 0 or b1 = 0, return 0; without conditional branch
  negs r5, r4         @ r5 = -a1 hex(256-dec(a1))

  # @ asrs rd, <#imm> --> #imm: 0-31
  # movs r6, #32        @ r6 = #32
  asrs r5, r6         @ r5 = -a1 >> 32

  ands r5, r7         @ r5 = tmp = b1 & (-a1 >> 32)
  negs r5, r5         @ r5 = -tmp

  # @ asrs rd, <#imm> --> #imm: 0-31
  asrs r5, r6         @ r5 = -tmp >> 32

  ands r3, r5         @ r3 = s & (-tmp >> 32) = (a1 * b1)
  

  mov  r1, r8         @ r1 = &c

  @@@@ c1
  eors r3, r0         @ r3 =  [((a0 * b1) ^ rnd) ^ (a1 * b0)] ^ (a1 * b1)

  strb r1, [r1, #4]   @ Clearing the write bus, r1 = &c
  strb r3, [r1, #4]   @ Storing c1, r3 = c1


  
  nop
  nop
  nop
  nop


#  @ Trigger #########################################################################
  # Seperating instructions related to main function and trigger, as there are pipeline stages 

  @ Trigger
  @ scale.c: LPC13XX_GPIO1->GPIODATA &= ~( 0x1 <<  0 ) ; // initialise SCALE_GPIO_PIN_TRG = 0
  @ SCALE_GPIO_PIN_TRG in scale board: pin33: PIO1_0
  @ PIO1_0: https://www.digikey.pl/htmldatasheets/production/660585/0/0/1/lpc1311fhn33-551.html : 9.4 Register description
  @ baseaddress: 0x50010000, offset: 0x3ffc, baseaddress: 0x50010000, offset: 0x3ffc
  @ address: 0x5001ffc; producing this value: needs several instructions:
  @ https://developer.arm.com/documentation/den0042/a/Unified-Assembly-Language-Instructions/Instruction-set-basics/Constant-and-immediate-values
  @ Creating Trigger:                                       _____
  @ changing the value in add 0x5001ffc (0 --> 1 --> 0) ___|     |____ 
  @
  @ (0 --> 1 : 14 insts (1 ldr + 1 str): 16 cycles --> 0)

  @ Start of trigger
  movs r4, #80
  lsls r4, r4, #8
  movs r5, #1
  eors r4, r5  //0x5001
  lsls r4, #16 //0x50010000
  movs r5, #63 //0x3f
  lsls r5,r5,#8 //0x3f00
  eors r4,r5    //0x50013f00
  movs r5, #252
  eors r4,r5    //0x50013ffc
  movs r5,#1
  ldr  r6, [r4, #0]  @ r6 = 0 : SCALE_GPIO_PIN_TRG = 0
  # test: str  r6, [r3, #0]  @ r6 = 0xfc0f0000
  eors r5, r6  @ r5 = 1 @ Start trigger: SCALE_GPIO_PIN_TRG = 1
  str  r5, [r4, #0]
  # test: str  r5, [r3, #4] @ r6 = 0xfd0f0000
  nop
  nop
  nop
  nop
  str  r6, [r4, #0] @ End trigger: r6 = 0 : SCALE_GPIO_PIN_TRG = 0
  # test: str  r6, [r3, #8] @ r6 = 0xfc0f0000


  pop  {r4-r7}
  mov   r8, r4
  mov   r9, r5
  mov   r10, r6
  mov   r11, r7
  pop   {r4-r7}
  pop  {pc}
  .endfunc 


.end
