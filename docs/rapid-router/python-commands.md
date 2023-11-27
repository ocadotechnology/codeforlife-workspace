---
description: Useful Python commands to use in the later levels of Rapid Router
---

# Python Commands

Run the following commands on the van object v, e.g. `my_van.move_forwards()`

## **Movement**

```python
my_van.move_forwards()
my_van.turn_left()
my_van.turn_right()
my_van.turn_around()
my_van.wait()
```

## **Position**

```python
my_van.at_dead_end()
my_van.at_destination()
my_van.at_red_traffic_light()
my_van.at_green_traffic_light()
my_van.at_traffic_light(c)
# where c is 'RED' or 'GREEN'
```

```python
my_van.is_road_forward()
my_van.is_road_left()
my_van.is_road_right()
my_van.is_road(d)
# where d is 'FORWARD', 'LEFT', or 'RIGHT'
```
