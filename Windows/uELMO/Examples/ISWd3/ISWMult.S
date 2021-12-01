.syntax unified
.text
.thumb


.global ISWd3
.func ISWd3
ISWd3:
//Appendix B, from "How Fast Can Higher-Order Masking Be in Software?"
push {r4-r7}
mov r4, r8
mov r5, r9
mov r6, r10
mov r7, r11
push {r4-r7}
movs r7, #0		//temp
mov r8, r7		//a2
mov r9, r7		//a3
mov r10, r7		//b2
mov r11, r7		//b3

ldr  r6, [r1, #4]	
mov  r8, r6		//a2
ldr  r7, [r1, #8]	
mov  r9, r7		//a3
ldr  r2, [r1, #12]	//b1
ldr  r6, [r1, #16]	
mov  r10, r6		//b2
ldr  r7, [r1, #20]	
mov  r11, r7		//b3
ldr  r1, [r1, #0]	//a1

movs r7, #0
    @Start of trigger
   @Trigger address: 0xE0000004
   movs r4, #224
   lsls r4, r4, #24
   adds r4, r4, #4
   movs r6, #1
   str  r6, [r4]	//Starttrigger
   nop
   nop						//0-250			        					      					
   //3-share ISW multiplication started:
   //Step 1: ci=ai*bi
   mov  r3, r2		//c1=b1			0-250
   mov  r6, r8		//t2=a2			250-500
   mov  r4, r10		//c2=b2			500-750
   mov  r7, r9		//t2=a3			750-1000
   mov  r5, r11		//c3=b3			1000-1250
   ands r5, r7		//c3=a3*b3		1250-1500
   ands r4, r6		//c2=a2*b2		1500-170
   ands r3, r1		//c1=a1*b1


   //Step 2: add randomness
   //i=1,j=2
   ldr  r7, [r0, #0]	//t2=r12
   eors r3, r7		//c1=c1+r12
   mov  r6, r10		//t1=b2
   ands r6, r1		//t1=a1*b2
   eors r7, r6		//s'=(r12+a1*b2)
   mov  r6, r8		//t1=a2
   ands r6, r2		//t1=a2*b1
   eors r7, r6		//s'=((r12+a1*b2)+a2*b1)
   eors r4, r7		//c2=c2+s'

   //i=1,j=3
   ldr  r7, [r0, #4]	//t2=r13 
   eors r3, r7		//c1=c1+r13
   mov  r6, r11		//t1=b3		
   ands r6, r1		//t1=a1*b3	
   eors r7, r6		//s'=(r13+a1*b3)	
   mov  r6, r9		//t1=a3	
   ands r6, r2		//t1=a3*b1
   eors r7, r6		//s'=((r13+a1*b3)+a3*b1)
   eors r5, r7		//c3=c3+s' 	

   //a1 and b1 can be deleted now, so r1=b3, r2=a3
   mov  r1, r11
   mov  r2, r9
   //i=2,j=3
   ldr  r7, [r0, #8]	//temp=r23 
   eors r4, r7		//c2=c2+r23
   mov  r6, r8		//t1=a2	
   ands r6, r1		//t1=a2*b3	
   eors r7, r6		//s'=(r23+a2*b3)	
   mov  r6, r10		//t1=b2	
   ands r6, r2		//t1=a3*b2
   eors r7, r6		//s'=((r23+a2*b3)+a3*b2)
   eors r5, r7		//c3=c3+s'


   //store
   str r3, [r0,#0]
   str r4, [r0,#4]
   str r5, [r0,#8]
   @End of trigger
   @Trigger address: 0xE0000004
   movs r4, #224
   lsls r4, r4, #24
   adds r4, r4, #4
   movs r6, #0
   str  r6, [r4]	//Endtrigger

 //45C
pop {r4-r7}
mov r8, r4
mov r9, r5
mov r10, r6
mov r11, r7
pop {r4-r7}
bx lr

.endfunc
.global ISWd3_leak
.func ISWd3_leak
ISWd3_leak:
//Appendix B, from "How Fast Can Higher-Order Masking Be in Software?"
push {r4-r7}
movs r7, #0		//temp
mov r8, r7		//b1
mov r9, r7		//a3
mov r10, r7		//b2
mov r11, r7		//b3

ldr  r6, [r1, #12]	
mov  r8, r6		//b1
ldr  r7, [r1, #8]	
mov  r9, r7		//a3
ldr  r2, [r1, #4]	//a2
ldr  r6, [r1, #16]	
mov  r10, r6		//b2
ldr  r7, [r1, #20]	
mov  r11, r7		//b3
ldr  r1, [r1, #0]	//a1


   @Start of trigger
   @Trigger address: 0x50013FFC
   movs r5, #80
   lsls r5, r5, #8
   adds r5, r5, #1
   lsls r5, r5, #16
   movs r6, #63
   lsls r6,r6,#8
   eors r5,r6
   movs r6, #252
   eors r5,r6
   movs r6,#1
   ldr  r4, [r5, #0]
   eors r6, r4
   str  r6, [r5, #0]
   nop
   nop
   nop
   nop	
   str  r4, [r5, #0]  
   nop						//0-250
   nop			        	            		           				
   //3-share ISW multiplication started:
   //Step 1: ci=ai*bi
   movs r3, r2		//c1=a2			0-250
   mov  r6, r8		//t2=b1			250-500
   mov  r4, r10		//c2=b2			500-750
   mov  r7, r13		//t2=a3			750-1000
   nop						//0-250
   nop
   mov  r5, r11		//c3=b3			1000-1250
   ands r5, r7		//c3=a3*b3		1250-1500
   ands r4, r3		//c2=a2*b2		1500-170
   ands r6, r1		//c1=a1*b1
   mov  r3, r6


   //Step 2: add randomness
   //i=1,j=2
   ldr  r7, [r0, #0]	//t2=r12
   eors r3, r7		//c1=c1+r12
   mov  r6, r10		//t1=b2
   ands r6, r1		//t1=a1*b2
   eors r7, r6		//s'=(r12+a1*b2)
   mov  r6, r8		//t1=b1
   ands r6, r2		//t1=a2*b1
   eors r7, r6		//s'=((r12+a1*b2)+a2*b1)
   eors r4, r7		//c2=c2+s'

   //i=1,j=3
   ldr  r7, [r0, #4]	//t2=r13 
   eors r3, r7		//c1=c1+r13
   mov  r6, r11		//t1=b3		
   ands r6, r1		//t1=a1*b3	
   eors r7, r6		//s'=(r13+a1*b3)	
   mov  r6, r9		//t1=a3	
   mov  r1, r8		//r1=b1
   ands r6, r1		//t1=a3*b1
   eors r7, r6		//s'=((r13+a1*b3)+a3*b1)
   eors r5, r7		//c3=c3+s' 	

   //a1 and b1 can be deleted now, so r1=b3
   mov  r1, r11
   //i=2,j=3
   ldr  r7, [r0, #8]	//temp=r23 
   eors r4, r7		//c2=c2+r23
   mov  r6, r1
   ands r6, r2		//t1=a2*b3	
   eors r7, r6		//s'=(r23+a2*b3)
   mov  r1, r9          //r1=a3	
   mov  r6, r10		//t1=b2	
   ands r6, r1		//t1=a3*b2
   eors r7, r6		//s'=((r23+a2*b3)+a3*b2)
   eors r5, r7		//c3=c3+s'
   nop
   nop
   nop
   nop
   nop
   nop

   //store
   //str r3, [r0,#0]
   //str r4, [r0,#4]
   //str r5, [r0,#8]


 

pop {r4-r7}
bx lr

.endfunc
.end
