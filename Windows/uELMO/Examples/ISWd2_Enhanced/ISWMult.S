.syntax unified
.text
.thumb


.global ISWd2
.func ISWd2
ISWd2:
//r0=address of input
//r1=address of random
//r2=address of output
  nop
  nop
push {r4-r7}
mov  r7, r9
push {r7}
movs r7, #0		//temp
mov r3, r7
mov r4, r7
mov r5, r7	
mov r6, r7	
mov r9, r7		
	
				
   @Start of trigger
   @Trigger address: 0xE0000004
   movs r7, #224
   lsls r7, r7, #24
   adds r7, r7, #4
   movs r6, #1
   str  r6, [r7]	//Starttrigger
   nop
   nop
   nop				//	0-250
   //save r2
   mov r9, r2			//	250-500
   //Load operands
   ldr r5, [r1, #0]	//r5=r		//	500-750
   ldr r1, [r0, #0]	//r1=a1		//	750-1000
   ldr r3, [r0, #8]	//r3=b1		//	1000-1250
   ldr r2, [r0, #4]	//r2=a2		//	1250-1500
   ldr r4, [r0, #12]	//r4=b2		//	1500-2000				
   //2-share ISW multiplication started:
   //Step 1: ci=ai*bi
   mov  r6, r1		//c1=a1		2000-2250	
   ands r6, r3		//c1=a1*b1	2250-2500
   mov  r7, r4		//c2=b2		2500-2750	

   //Step 2: add randomness
   //i=1,j=2
   ands r1, r4		//r1=a1*b2				2750-3000	
   eors r1, r5		//r1=a1*b2+r				3000-3250
   ands r7, r2		//c2=b2*a2				3250-3500
   eors r7, r5		//c2=a2*b2+r				3500-3750
   ands r2, r3		//r2=a2*b1				3750-4000
   eors r1, r2		//r1=(a1*b2+r)+a2*b1			4000-4250
   eors r6, r1		//c1=a1*b1+((a1*b2+r)+a2*b1)		4250-4500
   movs	r2, r0
   mov r2, r9		//Get back r2				4500-4750    //port A HD=a1b1--->a2
   nop			//					4750-5000
   nop			//					5000-5250
   //store
   str r6, [r2,#0]	//					5250-5500
   str r2, [r2,#4]      //					5500-5750
   str r7, [r2,#4]	//					5750-6000
nop
nop
   @End of trigger
   @Trigger address: 0xE0000004
   movs r7, #224
   lsls r7, r7, #24
   adds r7, r7, #4
   movs r6, #0
   str  r6, [r7]	//Endtrigger

pop {r7}
mov  r9, r7
pop {r4-r7}
bx lr

.endfunc
.end
