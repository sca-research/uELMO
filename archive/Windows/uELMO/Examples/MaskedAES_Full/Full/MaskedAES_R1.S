##
## University of Bristol – Open Access Software Licence
## Copyright (c) 2016, The University of Bristol, a chartered
## corporation having Royal Charter number RC000648 and a charity
## (number X1121) and its place of administration being at Senate
## House, Tyndall Avenue, Bristol, BS8 1TH, United Kingdom.
## All rights reserved
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
## 1. Redistributions of source code must retain the above copyright
## notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above
## copyright notice, this list of conditions and the following
## disclaimer in the documentation and/or other materials provided
## with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
## FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
## COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
## INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
## SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
## OF THE POSSIBILITY OF SUCH DAMAGE.
##
## Any use of the software for scientific publications or commercial
## purposes should be reported to the University of Bristol
## (OSI-notifications@bristol.ac.uk and quote reference 2668). This is
## for impact and usage monitoring purposes only.
##
## Enquiries about further applications and development opportunities
## are welcome. Please contact elisabeth.oswald@bristol.ac.uk
##

  .syntax unified
  .text
  .thumb
  
  .extern S
  .extern MaskedS
  .extern xtime
  .extern rcon

  .extern U
  .extern V
  .extern UV
  .extern SRMask

.global GenMaskedSbox
.func GenMaskedSbox
GenMaskedSbox:
  push {lr}
  push {r0-r7}

  ldr r0, =U
  ldrb r1, [r0]
  ldr r0, =V
  ldrb r2, [r0]
  @r1=U, r2=V
  @Create variable UV

  ldr r0, =UV
  eors r2, r1
  strb r2, [r0]
  @UV=V^U=r2
  movs r3, #255
  ldr r4, =S
  ldr r5, =MaskedS
 masksbox:		@Create masked table
  mov r0, r2
  eors r0, r3		@r0=UV^i
  ldrb r6, [ r4, r0]	@r6=S[UV^i]
  eors r6, r1		@r6=S[UV^i]^U
  strb r6, [ r5, r3 ]	@MS[i]=S[UV^i]^U

  subs r3, #1		@i--
  bge.n masksbox
  
  pop {r0-r7}
  pop {pc}
  .endfunc


.global MaskingPlaintext
.func MaskingPlaintext

MaskingPlaintext:
  push {lr}
  push {r4-r7}

  ldr r3, =U
  ldrb r3, [r3]		@r3=U

  # Arrange data and key so they can be loaded in words
  movs r5, #15
arrangedatamasked:	@change the byte order to AES column first order, masked them with U at the same time
  lsls r6, r5, #2	@r6=(r5)<<2
  movs r7, #0x0C	@r7=0x0c
  ands r6, r7		@r6=(r5) low two bits in the last nibble
  lsrs r7, r5, #2	@r7=(r5)>>2
  eors r6, r7		@r6=(r5) low two bits in the last nibble||(r5) high two bits in the last nibble 
  ldrb r7, [r0, r6]	@load input to r7
  eors r7, r3		@mask input with U
  movs r4, #3
  ands r4, r5           @low 2 bits of r5
  strb r7, [r1, r5]	@store the masked value to output
  subs r5, #1		@proceed to other bytes
  bge.n arrangedatamasked

  pop {r4-r7}
  pop {pc}
  .endfunc

.global MaskingKey
.func MaskingKey
MaskingKey:
  push {lr}
  push {r0-r7}

  ldr r3, =V
  ldrb r2, [r3]

  movs r5, #15
arrangedatakeymasked:	@change the byte order to AES column first order, masked them with V at the same time
  lsls r6, r5, #2
  movs r7, #0x0C
  ands r6, r7
  lsrs r7, r5, #2
  eors r6, r7
  ldrb r7, [r0, r6]
  eors r7, r2
  strb r7, [r1, r5]	@store the masked key to output
  subs r5, #1
  bge.n arrangedatakeymasked
  
  pop {r0-r7}
  pop {pc}
  .endfunc  

.global MADK
.func MADK
MADK:
  push {lr}
  push {r4-r7}

   movs r4, #3		@r4=i
ADK:  
  lsls r5, r4, #2					//0-250			//2750-3000
  @ADK
  ldr r6, [r0, r5]     @r6=p(r4)			//250-750		//3000-3500
  ldr r7, [r1, r5]	@r7=k(r4)			//750-1000		//3750-4000
  eors r7, r6						//1000-1250
  str r7, [r0, r5]	@store it in masked output	//1250-1750
  subs r4, #1						//1750-2000
  bge.n ADK						//2000-2750

  pop {r4-r7}
  pop {pc}
  .endfunc  

.global MSbox
.func MSbox
MSbox:
  push {lr}
  push {r0-r7}

  movs r4, #15		@r4=i
  ldr r5, =MaskedS	@r5=MaskedS			//0-250
  ldr r1, =S						//250-500

MS:  
  @SBox
  ldrb r6, [r0, r4]     @r6=input(r4)			//500-1000	//2500-3000	//4500-4750

  ldrb r3, [r5, r6]	@r3=MaskedS(r6)=S(sum)^U	//1000-1250	//3000-3250	//4750-5000
  strb r3, [r0, r4]	@store it in masked output	//1250-1500	//3250-3500	//5250-5500

  subs r4, #1						//1500-1750	//3500-3750
  bge.n MS						//1750-2500	//3750-4500

  pop {r0-r7}
  pop {pc}
  .endfunc 


.global MShiftRow
.func MShiftRow
MShiftRow:
  push {lr}
  push {r4-r7}


  movs r5, #8			//
  movs r6, #16			//0-250
  movs r7, #24			//250-500

  ldr r4, [ r0, #4 ]		//500-1000
  rors r4, r5 			//1000-1250
  str r4, [ r0, #4 ]		//1250-1750

  ldr r4, [ r0, #8 ]		//1750-2250	
  rors r4, r6 			//2250-2500
  str r4, [ r0, #8 ]		//2500-3000

  ldr r4, [ r0, #12 ]		//3000-3500
  rors r4, r7 			//3500-3750
  str r4, [ r0, #12 ]		//3750-4250

  pop {r4-r7}
  pop {pc}
  .endfunc

  

.global MMixColumn
.func MMixColumn
MMixColumn:

  push {lr}
  push {r0-r7}  

  movs r3, #0	@Clear Context
  movs r4, #0
  movs r5, #0
  movs r6, #0
  movs r7, #0

  mov r2, r8
  push {r2}
  mov r2, r9
  push {r2}
  mov r2, r10
  push {r2}


  mov r9, r0		@input
  mov r8, r1		@output

  ldr r7, =xtime_const
  ldr r5, =V
  ldrb r3, [r5]       
  ldr r5, =xtime
  ldrb r6, [r5, r3]
  //r3=V,r6=2V
  
  lsls r5, r6, #8	
  eors r6,r5		//r6=2V||2V
  lsls r5, r6, #16
  eors r6, r5		//r6=2V||2V||2V||2V
  lsls r5, r3, #8
  eors r3, r5
  lsls r5, r3, #16
  eors r3, r5		//r3=V||V||V||V

  movs r4, #3
mix_columnmasked:
  mov r10, r4  		//r10=i
  mov r0, r4		//r0=i
  mov r4, r9		//r4=input
  lsls r1, r0, #2	//r1=i<<2
  ldr r1, [r4, r1]	//r1=input[i<<2]
  adds r0, #1		//r0=i+1
  movs r4, #3		//r4=3
  ands r0, r4		//r0=(i+1)&0x3
  mov r4, r9		//r4=input
  lsls r5, r0, #2	//r5=(i+1)&0x3<<2
  ldr r5, [r4, r5]	//r5=input[(i+1)&0x3<<2]
  eors r1, r3		//r1=input[i<<2]^(V||V||V||V)
  eors r1, r5		//r1=input[i<<2]^(V||V||V||V)^input[(i+1)&0x3<<2]
  lsrs r4, r1, #7	//r4=input[i<<2]^input[(i+1)&0x3<<2]^(V||V||V||V)>>7
  ldr r2, [r7, #0]	//r2=0x01010101
  ands r4, r2		//r4=(input[i<<2]^input[(i+1)&0x3<<2]^(V||V||V||V)>>7)&0x01010101
  ldr r2, [r7, #8]	//r2=0x1B
  muls r4, r2		//r4=r4*r2
  lsls r1, r1, #1	//r1=(input[i<<2]^input[(i+1)&0x3<<2]^(V||V||V||V)<<1)
  ldr r2, [r7, #4]	//r2=0xFEFEFEFE
  ands r1, r2		//r1=(input[i<<2]^input[(i+1)&0x3<<2]^(V||V||V||V)<<1)&0xFEFEFEFE
  eors r1, r4		//r1=2*(input[i<<2]^input[(i+1)&0x3<<2]^(V||V||V||V))
  eors r1, r5		//r1=2*(input[i<<2]^input[(i+1)&0x3<<2]^(V||V||V||V))^input[(i+1)&0x3<<2]
  adds r0, #1		//r0=(i+1)&0x3+1
  movs r4, #3		
  ands r0, r4		//r0=((i+1)&0x3+1)&0x3
  mov r4, r9		//r4=input
  lsls r5, r0, #2	//r5=r0<<2
  ldr r5, [r4, r5]	//r5=input[((i+1)&0x3+1)&0x3<<2]
  eors r1, r5		//
  adds r0, #1
  movs r4, #3
  ands r0, r4
  mov r4, r9
  lsls r5, r0, #2
  ldr r5, [r4, r5]
  eors r1, r5
  eors r1, r6
  mov r5, r10
  lsls r5, r5, #2
  mov r0, r8
  str r1, [r0, r5]
  mov r4, r10
  subs r4, #1
  bge.n mix_columnmasked//54

  pop {r2}
  mov r10, r2
  pop {r2}
  mov r9, r2
  pop {r2}
  mov r8, r2
 
  pop {r0-r7}
  pop {pc}
  .endfunc

.global Finalize
.func Finalize
Finalize:
  push {lr}
  push {r0-r7}

  ldr r2, =SRMask@Additional Mask that proteced SR
  ldr  r4, =UV
  ldrb r3, [r4]
  movs r5, #15
Fin:	@change the byte order to AES column first order, masked them with U at the same time
  lsls r6, r5, #2	@r6=(r5)<<2
  movs r7, #0x0C	@r7=0x0c
  ands r6, r7		@r6=(r5) low two bits in the last nibble
  lsrs r7, r5, #2	@r7=(r5)>>2
  eors r6, r7		@r6=(r5) low two bits in the last nibble||(r5) high two bits in the last nibble 
  ldrb r7, [r0, r6]	@load input to r7
  eors r7, r3		@mask input with U
  movs r4, #3
  ands r4, r6           @r4=low 2 bits of r6
  ldrb r4, [r2, r4]     @r4=SRMask[r6&0x0011]
  eors r7, r4           @r7=r7^SRMask[r6&0x0011]
  strb r7, [r1, r5]	@store the masked value to output
  subs r5, #1		@proceed to other bytes
  bge.n Fin

  pop {r0-r7}
  pop {pc}
.endfunc


.global SafeCopy
.func SafeCopy
SafeCopy:
  push {lr}
  push {r2-r6}

  movs r3, #0
loop:
  movs r2, #0 @Zero reg & bus
  lsls r4, r3, #2
  str r2, [r1, r4]
  ldr r2, [r1, r4]

  ldr r2, [r0, r4]@Load value
  str r2, [r1, r4]@Store value
  adds r3, #1
  cmp  r3, #4
  bne  loop

  pop {r2-r6}
  pop {pc}
.endfunc
  .end
