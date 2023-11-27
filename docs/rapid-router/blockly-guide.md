---
description: Blockly - Python guide for Rapid Router
---

# Blockly Guide

## Van starting block

![](<../.gitbook/assets/Screenshot 2021-05-28 at 11.43.56.png>)

```python
from van import Van
my_van = Van()
```

The starting code has been created ‘behind the scenes‘ in Python and has to be imported.

Those two lines are therefore automatically added to your new program in Rapid Router. When you open the Python pane, you should see this code. These two lines are required before all other commands.

After this code, the van object, which is the object controlling van movement on the map, is indicated by the variable `my_van`.

You could change the name of this object to whatever you like, but be consistent and use the same name with the commands afterwards.

## Move forwards, turn left, turn right

![](<../.gitbook/assets/Screenshot 2021-05-28 at 11.53.22 (1).png>)

```python
my_van.move_forwards()
my_van.turn_left()
my_van.turn_right()
```

`move_forwards`, `turn_left` and `turn_right` are, in fact, procedures. Once called, they cause the van to move. This is why when we want the van to move forwards, we call its `move_forwards` procedure by putting () after its name (e.g. `my_van.move_forwards()`)

Note the underscore (“\_”) is an essential part of the name.

## Repeat n times

![](<../.gitbook/assets/Screenshot 2021-05-28 at 11.57.54.png>)

```python
for number in range(n):
```

This code will repeat all commands indented underneath it `n` times, where `n` is a whole number such as 3. It works with any name inserted where the word number is shown in the example. (The built-in range function just tells the loop how many times to repeat.)

```python
for count in range(3):
    my_van.move_forwards()
```

The example on the left would repeat `my_van.move_forwards()` 3 times. You can use the count variable inside the body of the loop if you want the van’s behaviour to differ depending on how many times the for loop was executed. On the first time through the loop, its value will be 0, incremented by one each time around the loop.

You must use a colon `:` at the end of the `for` line because this indicates that a sequence of instructions should follow (we call them the body of the loop). These instructions must all be indented by the same amount (ideally by 4 spaces).

## Wait

![](<../.gitbook/assets/Screenshot 2021-05-28 at 12.08.17.png>)

```python
my_van.wait()
```

A procedure which when executed or ‘called’, causes the van to wait.

## If, else if and else

![](<../.gitbook/assets/Screenshot 2021-05-28 at 12.26.47 (1).png>)

```python
if my_van.is_road(‘FORWARD’):
    my_van.move_forwards()
elif my_van.is_road(‘LEFT’):
    my_van.turn_left()
else:
    my_van.turn_right()
```

The indentation of the instructions inside a block must match. Ideally, they would be indented 4 spaces more than the previous statement.

`if`, `elif` and `else` statements must all be indented to the same level as each other, and all require a colon `:` at the end of their statement.

{% hint style="info" %}
`elif` is short for `else if`
{% endhint %}

![](<../.gitbook/assets/Screenshot 2021-05-28 at 12.32.23.png>)

```python
if my_van.at_traffic_light(‘RED’):
    my_van.wait()
```

The example to the left will cause the van to wait if it is currently at a red traffic light.

## Conditions

![](<../.gitbook/assets/Screenshot 2021-05-28 at 16.46.28.png>)

```python
my_van.is_road(‘FORWARD’)
my_van.is_road(‘LEFT’)
my_van.is_road(‘RIGHT’)
my_van.at_traffic_light(‘RED’)
my_van.at_traffic_light(‘GREEN’)
```

These conditions can be added after an `if`, `elif` or `else` statement.

Each of the conditions are functions that check the state the van is in (i.e. what kind of road is ahead or what colour the traffic light is) and returns `True` or `False`.

{% hint style="info" %}
If a variable can only be True or False, it is called a “Boolean”.
{% endhint %}

## Repeat until at destination

![](<../.gitbook/assets/Screenshot 2021-05-28 at 16.53.01.png>)

```python
while not my_van.at_destination():
    my_van.move_forwards()
```

The `while` not statement repeats until the condition is `True`.

Remember the colon denotes a set of instructions to be followed if the `while` condition is met (we call it the body of the loop).

## Repeat while traffic light is red

![](<../.gitbook/assets/Screenshot 2021-05-28 at 16.57.55.png>)

```python
while my_van.at_traffic_light(‘RED’):
    my_van.wait()
```

These instructions must be consistently indented, ideally by 4 spaces.

This example will cause the van to wait until the traffic lights are no longer red.

## Procedures

![](<../.gitbook/assets/Screenshot 2021-05-28 at 17.03.11.png>)

```python
def procedurename():
```

To create a procedure, you use the `def` keyword. The procedure needs a meaningful name where `procedurename` is placed in the example. You must have a pair of brackets () and a colon `:` after it.&#x20;

```python
def proc1():
    my_van.turn_left()
    my_van.turn_right()
    
proc1()
```

All subsequent statements that are to be part of the procedure must be indented to the same level as each other (ideally 4 spaces).

The procedure is then executed (or called), by typing the name of the procedure followed by a pair of brackets ().

In this example, the proc1 procedure will move the van left and then right when called. In reality, it is better to choose a more meaningful name for your procedure.

```python
def forward_left(n):
    for count in range(n):
        my_van.move_forwards()
        my_van.turn_left()
        
forward_left(4)
```

What happens inside the procedure can be changed each time by passing in arguments. Arguments available to the procedure are defined in between the two brackets, such as the argument n in this example. This value is then used to change how many times the loop is executed.

When calling a procedure with an argument, you must define the value for that argument when you call the procedure. In this case, we are calling the forward\_left procedure with the argument value of 4, which means the loop will execute 4 times (the van will move forward 4 times before turning left).

##
