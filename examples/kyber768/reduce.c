#include <stdint.h>
#include "params.h"
#include "reduce.h"

/*************************************************
* Name:        montgomery_reduce
*
* Description: Montgomery reduction; given a 32-bit integer a, computes
*              16-bit integer congruent to a * R^-1 mod q,
*              where R=2^16
*
* Arguments:   - int32_t a: input integer to be reduced;
*                           has to be in {-q2^15,...,q2^15-1}
*
* Returns:     integer in {-q+1,...,q-1} congruent to a * R^-1 modulo q.
**************************************************/
int16_t montgomery_reduce(int32_t a)
{
    int32_t t;
    int16_t u;

    u = a * QINV;
    t = (int32_t) u *KYBER_Q;
    t = a - t;
    t >>= 16;

    return t;
}

/*************************************************
* Name:        barrett_reduce
*
* Description: Barrett reduction; given a 16-bit integer a, computes
*              16-bit integer congruent to a mod q in {0,...,q}
*
* Arguments:   - int16_t a: input integer to be reduced
*
* Returns:     integer in {0,...,q} congruent to a modulo q.
**************************************************/
int16_t barrett_reduce(int16_t a)
{
    int16_t t = 0;
    const int32_t v = ((1U << 26) + KYBER_Q / 2) / KYBER_Q;

    int32_t at = 0;

    asm volatile ("SXTH %0, %1":"+r" (at):"r"(a):);
    at = (v * at) >> 26;
    asm volatile ("MOV %0, %1":"+r" (t):"r"(at):);

    t *= KYBER_Q;

    return a - t;
}

/*************************************************
* Name:        csubq
*
* Description: Conditionallly subtract q
*
* Arguments:   - int16_t x: input integer
*
* Returns:     a - q if a >= q, else a
**************************************************/
int16_t csubq(int16_t a)
{
    a -= KYBER_Q;
    a += (a >> 15) & KYBER_Q;
    return a;
}
