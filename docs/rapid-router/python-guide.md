---
description: Python guide for things that have no Blockly equivalence
---

# Python Guide

## Outputting text

```python
print (‘message’)
```

This will display whatever you put in the place of message in the Rapid Router Output console. You should surround your message with single quotes.

## Variables

```python
var_1 = ‘Hello!’ 
var_2 = var_1 
n = 1
```

You can create your own variables using any name except those on the reserved list below. You can assign values to variables using the “=” operator. You can assign the value of one variable to another variable.

You can use the variables anywhere in your program that you would normally use whatever the variable stands for.

## Mathematical operators

```python
n = 2 + 3 
n = 2 – 3 
n = 2 * 3 
n = 2 / 3
```

You can use these with numbers or numeric variables or both.

The examples show addition, subtraction, multiplication and division.

With division, note that the result will be rounded down. For example, the following: `n = 5 / 2`

The value of `n` will be 2, not 2.5.

## Exit a loop early

```python
while condition:
    break
```

Instead of waiting until `condition` is no longer `True`, the break statement will stop executing the loop immediately.

## Skip to the next time round the loop

```python
for count in range(5):
    continue
```

Instead of executing the rest of the commands in the loop, this statement will immediately move onto the next time around the loop.

## Do nothing

```python
pass
```

This statement does absolutely nothing. This is required if you want to define a procedure (or another block such as `for` or `while`) that has no other commands.

## Reserved words&#x20;

Reserved words are words that cannot be used as variable or procedure names as they are 'reserved' by Python:

```python
and
asset
break
class
continue
def
del
elif
else
except
exec
finally
for
from
global
if
import
in
is
not
or
pass
print
raise
return
try
while
with
```
