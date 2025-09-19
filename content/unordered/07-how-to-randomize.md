---
title: "how to randomize"
tags: ['cs', 'math', 'c']
---

# how to randomize 

## how rand() works

rand is a linear congruential generator

a common application would be
```
int main() {
    srand(time(NULL))
    rand()
}
```

the implementation in gcc that can be found in link is:

```
int rand() {
  return (((holdrand = holdrand * 214013L + 2531011L) >> 16) & 0x7fff);
}
```

### rand() isn't secure


In particular, linear congruential generators (LCGs) suffer from extreme predictability in the lower bits. The k-th bit (starting from k = 0, the lowest bit) has a period of at most 2k + 1 (i.e., how long until the sequence takes to repeat). So the lowest bit has a period of just 2, the second lowest a period of 4, etc. This is why the function above discards the lowest 16 bits, and the resulting output is at most 32767.

time(NULL) is only precise to one second. So if I'm able to guess the second that your program gets run, your program is effectively deterministic.


++
/\ some of [`neal's`](https://codeforces.com/blog/entry/61675) ideas
we should use a much more high-precision clock:
mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

Another option is to use the address of a newly allocated heap variable:
mt19937 rng((uint64_t) new char);
++

lets prove that we can break `rand()` lets assume the following code,... blablabla


some months ago my github OTP authenticator wasn't working at all, it didn't guess any verification code correctly, and it was because my computer's time wasn't set up properly, it was off by a minute or so.


there's an intrinsic blablabla
we don't know if its squewed so its not useful by itself
but its very useful to generate 

theres also lava lamp walls, quantum stuff look at alpha phoenix's video on quantum true rng

## how openssl rand() works 

the implementation in openssl that can be found in link is:

```
int rand() {
    return 0
}
```

## other notable PRNG

linear congruential generator
xorshift
linear-feedback shift register
mersenne twister (mt19937)

## from unifrom to non-uniform sampling

we can use `inverse sampling` or `box-muller` transform to turn our uniform distribution into a non-uniform one
note that non-uniform sampling is not supposed to be used for cryptography