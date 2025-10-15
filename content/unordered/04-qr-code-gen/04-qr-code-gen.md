---
title: "qr code generator"
tags: ['cs', 'math', 'project', 'python']
---

# building a qr code generator in python

`motivation:` ive read and implemented some of thonky's blog which is a stellar blog, but it lacks code and i also want to comment on some interesting facts about qr codes. and i also really want to talk about the maths involved.

the scope of this blog will be only the interesting that was missed in thonky's blog. im going to focus/go deeper into `data encoding` and `error correction encoding`.

## some background on qr codes

++
/\ the size of the qr code is reffered to as the `version`
qr code's have 2 main qualities;
1. the size of the qr code. e.g. $21\times 21, 25\times 25, ... , 177\times 177$
2. the error correction percentage, e.g. $L: 7\%, M :15\%, Q: 25\%, H: 30\%$
++

<div style="text-align: center">
    <div class="image-container">
        <img src="/files/qr-code-versions.png" alt="sudoku" width="800" height="200">
        <label class="image-caption">an image example of the different versions - <a href="https://www.researchgate.net/figure/Les-differentes-versions-du-code-QR-15-Structure-dun-code-QR_fig4_354573162">research gate</a></label>
    </div>
</div>

the amount of readable data that the qr code holds is based on both the qr code and the error correction, 
the error correction is defined as how much of the readable data bytes can be recuperated if lost,
the error correction bytes can even correct themselves!

the notion of error correction in qr codes allows for faster and more reliable qr code scanners,
and it also allows for some creativity: [6d qr code](https://altsoph.substack.com/p/qr-dice) 
[qr code art](https://research.swtch.com/qart).

++
/\ the qr code format was created in 1994 by the japanese company `Denso-Wave`.
the readable data of the qr code can be of 4 sources;
1. numeric, e.g. $'12312412'$, $'012312'$
2. alphanumeric, e.g. 'MYPA$$WORD123', $'10*1.4:'$
3. byte, e.g. 'Français', '∫x dx', '∆x😀🌹'
4. kanji, e.g. 'こんにちは'
++

++
/\ i will add images when we look at each step in depth, i don't want to create confusion right now
the idea is to fit your data to the data encoding that will result in the minimal number of bytes.
(the less data the more error correction we can fit. in the same qr code version).
ideally it would be optimal to link different modes for one text, meaning that for $HELLO-123$
it would be better to represent the $HELLO-$ as alphanumeric and the $123$ as numeric, but that requires `ECI` encodings which i might get into. TODO delve into ECI

then from the final data bytes to create an error correction encoding for it. the error correction works like magic, it finds where the errors are and fixes them. we will use [`reed-solomon`](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction) error correction

then the error correction bytes and the input bytes will each be placed into blocks and those blocks will be interleaved, structuring the final byte array that will represent the qr code's data.

then that data will be placed on the qr code matrix structure, together with the standard patterns that are the same for all qr codes, such as the $3$ blocks that define the orientation of the qr code.

because the matrix well get might have large black blobs that might make decoding difficult for qr code scanners, an array of masks will be used to mask the matrix and get the most decodeable looking qr code.

the final step is to add metadata. format (numeric, alphanumeric, ...), the qr code version (its size), the error correction level used, and the mask pattern used.
++

## data analysis

let's say we want to encode some text, ill show you how to encode numeric, alphanumeric, and bytes. i won't get into kanji, you can read on thonky's page [about it](https://www.thonky.com/qr-code-tutorial/kanji-mode-encoding).

++
/\ we could encode everything as byte code (`UTF-8`), but it would be inefficient. numbers $1$ through $9$ would be $0x31$ through $0x39$ (because the ascii table is the first thing in `UTF-8`), which is inefficient compared to $0x1$ through $0x9$.
you decide on the encoding, based on whats going to turn out as the minimal amount of bytes.
but because the formats are pretty different just finding the simplest encoding for your input is is enough.
++

kanji is easy to spot, and so is numeric. <br>
alphanumeric is "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./;" <br>
and byte is the rest (`UTF-8`, `ISO 8859-1`).

## data encoding

to encode a qr code, after we decided on the text, we need to decide on the error correction level.
the percentage means, how much of the qr code can be obfuscated / corrupted, but still be readable. obviously a higher error correction leads to a bigger qr code for the same amount of text.
lets say we want to encode $10*1.4:$ into our qr code, with 'M' error correction $(15\%)$.
now we gotta find the smallest qr `version` to house our data, to do that we use this [character capacities table](https://www.thonky.com/qr-code-tutorial/character-capacities) <br>
and look for the first version with our error correction, that can contain our input text.
we are encoding a string of $7$ alphanumeric characters, which is less than $20$ thus from the table `version` $1$ will be best.

the data the qr code will contain will be, 
1. the mode indicator
2. the character count indicator
3. encoded data + padding
4. terminator

### step 1

the mode indicator dicates which encoding we are using for the input, numeric, alphanumeric, byte mode, kanji, ECI. the values are the following, <br>
numeric -> 0001 <br>
alphanumeric -> 0010 <br>
byte mode -> 0100 <br>
kanji mode -> 1000 <br>
ECI mode -> 0111 <br>

in step $3$ ill explain how to exactly decide on which mode to use.

### step 2

the amount of characters that the QR code can house depends on the `error correction level` and the `version`.
the length of the character counter will be equal to the maximum possible characters that a specific QR code can house,

for versions $1$ through $9$,   N: $10$ bits, A: $9$ bits, B: $8$ bits, J: $8$ bits <br>
for versions $10$ through $26$, N: $12$ bits, A: $11$ bits, B: $16$ bits, J: $10$ bits <br>
for versions $27$ through $40$, N: $14$ bits, A: $13$ bits, B: $16$ bits, J: $12$ bits <br>

### step 3 

++
/\ note that the input is a string in base $10$, not in base $2$.
lets say the input is $1101010000101$ we know it has to be numeric.
first we split the input into groups of three $110\space 101\space 000\space 010\space 1$
each group can have either three, two or one elements.
the first groups necessarily have three elements and are encoded into $10$ bits,
the last group which may have either three, two or one elements,
will be encoded into $7$ bits if it has two elements, and $4$ bits if only one element.
++

$110 \rightarrow 0001101111$ <br>
$101 \rightarrow 0001100101$ <br>
$000 \rightarrow 0000000000$ <br>
$010 \rightarrow 0000001010$ <br>
$1\space\space\space\space \rightarrow 0001$ <br> 

<br>

++
/\ the table is of size $45$, we are just parsing the characters as base $45$ to get each pair's value
lets say the input is $10*1.4:$, to convert it to binary we will use the following [table](https://www.thonky.com/qr-code-tutorial/alphanumeric-table). we split the input string into character pairs, $10\space*1\space.4\space;$
and then for each pair we take the first character's value from the table, mutiply by $45$ and add the second character's value from the table

$10 \rightarrow 45$ <br>
$*1 \rightarrow 1756$ <br>
$.4\space\rightarrow 1894$ <br>
$:\space\space\space\space \rightarrow 44$ <br>
++

++
/\ we say $11$ bits because that's the maximum bits needed, $'::'_{45}=2024$, $\log_2(2024)=10.9829935747<11$
then convert each number to their 11 bit binary representation.

$45\space\space\space\space \rightarrow 00000101101$ <br>
$1756 \rightarrow 11011011100$ <br>
$1894 \rightarrow 11101100110$ <br>
$44\space\space\space\space \rightarrow 00000101100$ <br>
++

<br>

++
/\ `ISO 8859-1` [table](https://cs.stanford.edu/people/miles/iso8859.html) <br> `UTF-8` [table](https://www.charset.org/utf-8) <br><br>
/\ note that to encode `UTF-8` we need to use `UCI mode` and not `byte mode`
the default for byte mode is `ISO 8859-1`, which is an encoding that only uses one byte for each character, thus is only $256$ characters long. its bounded to the full keyboard + latin characters, it doesn't include all characters like `UTF-8` (e.g. emojis, chinese, japanese,...)
the `UTF-8` table and `ISO 8859-1` overlap on the first $256$ characters which is the range of the `ISO 8859-1` table,
but the difference is that `UTF-8` encodes the characters at range $128-255$ with two bytes instead of one.
if the input contains only characters of the full keyboard + latin, then we should use `ISO 8859-1`, otherwise `UTF-8` assumming the qr decoder we want to use supports it.
++

++
/\ `UTF-8` [lookup table](https://www.cogsci.ed.ac.uk/~richard/utf-8.html)
lets say the input is "∆x😀🌹", we know its byte code.
and we also know it has to be `UTF-8` because of the emojis.
we need to first convert each character to their hexadecimal value.
++

∆  $\space\space\space \rightarrow\space E2\space 88\space 86$ <br>
x  $\space\space\space \rightarrow\space 78$ <br>
😀 $\space \rightarrow\space F0\space 9F\space 98\space 80$ <br>
🌹 $\space \rightarrow\space F0\space 9F\space 8C\space B9$ <br>

then convert each hexa pair into an $8$ bit binary number.

$E2 \space 88\space 86 \space\space\space\space\space\space\space\space\rightarrow 11100010 \space 10001000 \space 10000110$ <br>
$78 \space\space\space\space\space\space\space\space\space\space\space\space\space\space\space\space\space\space\space  \rightarrow 01111000$ <br>
$F0 \space 9F\space 98\space 80 \space\space\rightarrow 11110000 \space 10011111 \space 10011000 \space 10000000$ <br>
$F0 \space 9F\space 8C\space B9 \rightarrow 11110000 \space 10011111 \space 10001100 \space 10111001$ <br>
<br>

### step 4 

let's say we are left with the binary string $"00000101101110110111001110110011000000101100"$, 
it could be possible that the string is too small for the qr code we want to use, so we need to pad the string. 
we need to pad (from the right) the binary string to have length that is a multiple of 8, we will use at most $7$ zeroes. the terminator is defined as the last $4$ binary zeroes used to pad the string, the terminator will be smaller if the binary input's length was 1,2, or 3 mod $8$.

++
/\ if we were encoding "∆x😀🌹" that is `UTF-8` we'd use `ECI mode` which is $0111$ and not `byte mode` which is $0100$
lets start creating a qr code with error correction level 'M', that will house the string $10*1.4:$.
which we know is alphanumeric. thus the encoding starts as 

$$0010$$
++

we know that we need a version 1 qr code, and we also know that the string is of length $7$.
so we need $9$ bits to encode the length which is $000000111$, thus the encoding is 

$$ 0010-000000111 $$

we know that $10*1.4:$ is encoded to binary as $"00000101101110110111001110110011000000101100"$. thus the encoding is 

$$ 0010-000000111-00000101101110110111001110110011000000101100 $$

the binary string is of length $57$ (without the dashes) meaning we need to pad it with $7$ zeroes.
and so the terminator is $0000$, and we add $3$ zeroes at the end aswell. thus the encoding is 

$$ 0010-000000111-00000101101110110111001110110011000000101100000-0000 $$

++
/\ the table's a bit out of order to me, but thats how thonky organized it
to calculate exactly how many bytes are left of padding we need to do the following calculation.
we now need a new table, the [`error correction table`](https://www.thonky.com/qr-code-tutorial/error-correction-table)
++
let's look at the first column, there for `1-M` we see the number $16$, meaning that our qr code should house $16$ bytes of information, which is much more than we have which is $8$ bytes.
all that's left to do is to pad the remaining $8$ bytes with $11101100\space 00010001$, so the encoding is 
 
$$
00100000\space 00111000\space 00101101\space 11011011\space 10011101\space 10011000\space 00010110\space 00000000 \\ 
11101100\space 00010001\space 11101100\space 00010001\space 11101100\space 00010001\space 11101100\space 00010001
$$

## error correction coding

we previously separated our encoding into bytes, from now on we are going to refer to each byte as a `data codeword`. to start generating the error correction, we are going to refer to the [`error correction table`](https://www.thonky.com/qr-code-tutorial/error-correction-table) once again.
you will see on columns $4$ through $7$ the mention of `blocks` and `group1`, `group2`.
the idea is to separate the `data codewords` (column $2$ ) into `groups` (columns $4$, $6$ ) and then to `blocks` (columns $5$, $7$ ), and later on create `error correction codewords` for each `block` (column $2$ ).

++
/\ for a more complicated example refer to [thonky](https://www.thonky.com/qr-code-tutorial/error-correction-coding)
for example, we generated data codewords for our qr code with `version` and `EC level` $1-M$,
thus we have $19$ codewords, $1$ block in group $1$, and $16$ data codewords in each block, and no second group.
meaning we don't have to split it at all.
++

so our group $1$ is defined by a singular block that is 

$$
00100000\space 00111000\space 00101101\space 11011011\space 10011101\space 10011000\space 00010110\space 00000000 \\ 
11101100\space 00010001\space 11101100\space 00010001\space 11101100\space 00010001\space 11101100\space 00010001
$$

we need to generate $10$ `EC codewords` for this block. <br>
to do so we are going to do operations over a `galois field`, specifically $GF(2^8)=GF(256)$. <br>
a field is a set with two operations, addition and multiplication. meaning an ordered triple $(F,+_F, \cdot_F)$, that satisfies the following.
1. $F$ is an abelian group under addition
2. $F \setminus \{0\}=F^*$ is an abelian group under multiplication
3. $F$ is distributive, $a\cdot (b+c) = a\cdot b + a\cdot c$

we define the galois field $GF(2^8)$ to be the set of elements from $0$ to $255$.
meaning elements represented by $8$ bits, and addressed as polynomials with binary coefficients.
with the following actions:

1. addition that is bit-wise modulo $2$, meaning a XOR.
2. multiplication to be polynomial multiplication modulo an irreducible polynomial of degree $8$ (modulo here means taking the remainder of long-division). <br>
where for two numbers $a,b\in GF(2^8)$ (numbers from $0$ to $255$ ), we represent them as polynomials at looking at their bit-wise representation as the coefficients for a degree $7$ polynomial, and the irreducible polynomial will be $x^8+x^4+x^3+x^2+1$ meaning with binary representation $100011101$
which is $285$. which is the same as long multiplication between $a, b$ where the addition is $XOR$ and after the calculation to do a modulo $285$ polynomial-wise.

note that $GF(2^8)$ is in fact a field because,
1. addition is symmetric and XOR only makes elements smaller not bigger, so its closed. it's also associative and the identity is $0$ and each element $a$ has an inverse which is $a$ meaning $a=-a$, because $a \oplus a = 0$.
2. multiplication is symmetric because polynomial multiplication is symmetric. and the identitiy is $1$ and each polynomial has an inverse modulo $x^8+x^4+x^3+x^2+1$ because of the `xgcd algorithm`, and the polynomial being `irreducible`. and polynomial multiplication is associative. and the multiplication of polynomials is closed because even though the multiplication can have a degree bigger than $8$, after doing modulo $x^8+x^4+x^3+x^2+1$, the remainder has to have degree $8$ or less which is in $GF(2^8)$ because it can be represented with $8$ bits or less.
3. $F$ is distributive because, $a\cdot_F (b +_F c) = a \cdot (b +_2 c) \mod m = (a\cdot b) +_2 (a\cdot c) \mod m = (a\cdot b \mod m) +_2 (a\cdot c \mod m) = (a \cdot_F b) +_F (a \cdot_F c)$ where $m = x^8+x^4+x^3+x^2+1$, and polynomial multiplication is distributive.

there is a much easier way to show that $GF(2^8)$ is a field, but i will get into that later.

++
/\ the multiplicative group is property $(2)$ of a field.
now let's show that $\langle 2\rangle =GF(2^8)^*$, meaning that $2$ is a generator for the multiplicative group of the galois field. meaning $\{2^0, 2^1, 2^2, 2^3, ... \} = \{2^{n-1} | n \in \mathbb{N}\}= GF(2^8)^*$
++
from group theory, the order of $G=\{2^{n-1} | n \in \mathbb{N}\}$ divides the order of $GF(2^8)^*$
because its a subgroup. because the order of $GF(2^8)^*$ is $|GF(2^8)|-1=256-1=255$
then the order of $G$ can be $1, 3, 5, 15, 17, 51, 85, 255$, let's prove manually that it's $255$.

++
/\ i tried to keep the numbers as $9$ bit at max $(< 512)$ so i could use the XOR, but i got lazy toward the end

$ 2^1=2 \neq 1$ <br>
$ 2^3=8 \neq 1$ <br>
$ 2^5=32 \neq 1$ <br>
$ 2^{15}=2^8\cdot 2^7 \neq 1$ <br>
$ 2^{17}=(2^8\cdot 2^4) \cdot 2^5 \equiv (205 \cdot 2) \cdot 2^4 = 135 \cdot 2^4 \equiv 19 \cdot 2^3 = 152 \neq 1$ <br>
$ 2^{51}=(2^8)^6\cdot 2^3 = ... = 10\neq 1$ <br>
$ 2^{85}=(2^8)^{10}\cdot 2^5 = ... = 214\neq 1$ <br> <br>
$ 2^8 = 2^8\oplus 285 \equiv 29 $ <br>
$ 2^8\cdot 2^4 \equiv 29\cdot 2^4 = 464 \equiv 464 \oplus 285 = 205 $ <br> 
 $ 205 \cdot 2 \equiv 410 \oplus 285 = 135 $ <br>
$ 135 \cdot 2 \equiv 170 \mod 285 = 19 $ <br> 

meaning that the order of the subgroup $G$ is $255$ meaning that it is equal to $GF(2^8)^*$, such that all the powers $\{2^0, 2^1, ..., 2^{255}\}$ are distinct and generate all elements in $GF(2^8)^*$.
later i will show how to prove that the subgroup has order $255$ much simply.
++

++
/\ in long-division the remainder will be $(a\cdot b) - 285$, because they have the same leading coefficient, and after one subtraction the long-division will stop. [long-division tutorial](https://www.youtube.com/watch?v=_FSXJmESFmQ). <br><br>
/\ thonky used the same [trick](https://www.thonky.com/qr-code-tutorial/error-correction-coding#step-5-generate-powers-of-2-using-bytewise-modulo-100011101) to create the [`log-antilog table`](https://www.thonky.com/qr-code-tutorial/log-antilog-table), 
when i calculated the values, i used the trick to simplify calculating $a\cdot b$ where $a\cdot b$ is a $9$ bit number. in the general case we would represent $a\cdot b$ as polynomial and calculate the remainder after long-division with $x^8+x^4+x^3+x^2+1$. but in this specific case, if $a\cdot b$ is a $9$ bit number, the remainder will be $(a\cdot b) \oplus 285$. <br>
why is that? that is because both $a\cdot b$, and $285$ are $9$ bits, thus in long-division the remainder will be $(a\cdot b) - 285$, and because we are in $GF(2^8)$ remember that each number is its own opposite, and addition is XOR, thus $a\cdot b \equiv (a\cdot b) \oplus 285$ making the calculations much easier.

because when we get an overflow after multiplication, it will only be by one bit and $x^8+x^4+x^3+x^2+1$ uses $9$ bits, then we will need to calculate $2^8\mod 285 \underset{\text{poly}}{\equiv} x^8 \mod x^8+x^4+x^3+x^2+1$, but because they have the same order, then the modulo is equal to the difference of the polynomials, meaning $x^8 \mod x^8+x^4+x^3+x^2+1 = x^8 - (x^8+x^4+x^3+x^2+1) = x^8 \oplus (x^8+x^4+x^3+x^2+1) = x^4+x^3+x^2+1 \underset{\text{poly}}{\equiv} 29$,
its straight-forward to show that in the general case, 
++





TODO:
irreducible, primitive, ring, maximal ideal, field.


$\langle x^8+x^4+x^3+x^2+1 \rangle$ is an ideal generated by a primitive polynomial, thus $GF(2^8)=GF(2)[x]/{\langle x^8+x^4+x^3+x^2+1 \rangle}$ is a field.

we will use the fact that the root of a primitive polynomial is a generator for the quotient generated by the polynomial. 
because $2$ is in its polynomial representation $x$, if we plot that into $x^8+x^4+x^3+x^2+1$ we get itself which is $0$ in modulo $x^8+x^4+x^3+x^2+1$. meaning that it's a root for the polynomial and thus is a generator for $GF(2^8)$.

we couldve chosen other polynomials instead of $x^8+x^4+x^3+x^2+1$, there are $16$ primitive polynomials of order $8$. i will show you how i arrived at that conclusion, and how to count polynomials.


## structure final message

## module placement in matrix

## data masking

## format and version information

## finite fields

## extension fields

### references:

1. [thonky's qr code tutorial](https://www.thonky.com/qr-code-tutorial/introduction)
2. [6d qr code](https://altsoph.substack.com/p/qr-dice) 
3. [qr code art](https://research.swtch.com/qart)