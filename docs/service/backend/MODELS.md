# Models

Below are the conventions we follow when modelling our data.

First, understand how to [define a Django model](https://docs.djangoproject.com/en/3.2/topics/db/models/).

## File Structure

TL;DR

- [x] One file per model in the `models` directory.
- [x] Each model-file follows the naming convention `{model}.py`.
- [x] Each model is imported from its file in `models/__init__.py`.
- [x] One test-file per model in the `models` directory.
- [x] Each model-test-file follows the naming convention `{model}_test.py`.
- [x] Each model-test-case follows the naming convention `Test{model}`.
- [x] Each model-test-case inherits `ModelTestCase`.
- [x] Each model-test-case set their type parameter to the model being tested.

---

For each model, create a file named after the model in the directory `models`.

```py
# models/person.py
class Person(WarehouseModel): ...
```

```py
# models/car.py
class Car(WarehouseModel): ...
```

All models should be imported into `models/__init__.py` to support importing multiple models from `models`.

```py
# models/__init__.py
from .car import Car
from .person import Person
```

```py
# some other py file can now import one or more models at a time.
from path.to.models import Car, Person
```

Any custom logic defined in a model-file should be tested in the directory `models`, where each model has its own test-file following the naming convention `{model}_test.py`. Model-tests should inherit `ModelTestCase` and set their type parameter to be the model they are testing. The name of the model-test-case should follow the convention `Test{model}`.

```py
# models/person_test.py
from codeforlife.tests import ModelTestCase

from ...models import Person

class TestPerson(ModelTestCase[Person]): ...
```

```py
# models/car_test.py
from codeforlife.tests import ModelTestCase

from ...models import Car

class TestCar(ModelTestCase[Car]): ...
```

## Warehousing Data

TL;DR

- [x] Inherit `WarehouseModel` if storing the model's historical data will provide meaningful insights.
- [x] Inherit `models.Model` if storing the model's historical data will NOT provide meaningful insights.

---

Determine whether the data stored in a model needs to be warehoused. Data should be warehoused if it can contribute to analyzing users' behavior. By default, new models should be warehoused as it's a rare occurrence that meaningful insights cannot be gained from analyzing its data.

Defining a model as a warehouse-model allows us to sync data from our database to our data warehouse before its deleted from our database. See our [data deletion strategy](https://code-for-life.gitbook.io/code-for-life-dev/data/storage#data-deletion-strategy).

Defining a warehouse-model:

```py
from codeforlife.models import WarehouseModel

class Example(WarehouseModel): ...
```

Defining a non-warehouse-model:

```py
from django.db import models

class Example(models.Model): ...
```

## Defining Fields

TL;DR

- [x] Always set `verbose_name`.
- [x] Always set `help_text`.

---

When defining fields of any type, always set the verbose name and help text. These arguments aid future developers and super-users on the Django admin to understand the purpose of these fields.

```py
from django.utils.translation import gettext_lazy as _

class CompanyMember(WarehouseModel):
  is_exec = models.BooleanField(
    verbose_name=_("is executive"),
    default=False,
    help_text=_(
      "Whether or not this company member is an executive member."
      " Executive members have elevated permissions to perform sensitive actions."
    ),
  )
```

## Defining Foreign Keys

TL;DR

- [x] Create type hints for backward relationships, such as `cars: QuerySet["Car"]`.
- [x] Import type hints for backward relationships inside of `if t.TYPE_CHECKING`.
- [x] Set `related_name` of the relationship to be the plural of the model's name.

---

When defining a foreign key between 2 models, a few steps need to be taken to inform our static type checker of backward relationships between objects.

Say we have the following models:

```py
# models/person.py
class Person(WarehouseModel):
  pass
```

```py
# models/car.py
from .person import Person

class Car(WarehouseModel):
  owner = models.ForeignKey(Person, on_delete=models.CASCADE)
```

From this we understand that an instance of `Car` has the attribute `owner` of type `Person`. [Django will create an attribute](https://docs.djangoproject.com/en/3.2/topics/db/queries/#following-relationships-backward) for "backward relationships" on each related object with the naming convention `{model}_set` at **runtime**. Therefore, `Person` has the attribute `car_set` which is a set of type `Car`.

The problem is static type checkers do not know attributes for backward relationships are going to being auto-generated. Therefore, we need to add type hints.

```py
# models/person.py
import typing as t

from django.db.models.query import QuerySet

if t.TYPE_CHECKING:
  from .car import Car

class Person(WarehouseModel):
  cars: QuerySet["Car"] 
```

```py
# models/car.py
from .person import Person

class Car(WarehouseModel):
  owner = models.ForeignKey(
    Person,
    on_delete=models.CASCADE,
    related_name="cars",
  )
```

We import the model we are type hinting inside of `if t.TYPE_CHECKING` to avoid circular-imports. We also define the name of the backward relationships to be the plural of the model's name to improve readability.

## Defining Meta Classes

Models' meta class should inherit `TypedModelMeta` to support type hinted Meta classes.

```py
from django_stubs_ext.db.models import TypedModelMeta

class Person(WarehouseModel):
  class Meta(TypedModelMeta): ...
```

## Defining Managers

TL;DR

If you're defining a model with a custom manager:

- [x] Define object manager as `Manager` within the model.
- [x] If the model inherits `WarehouseModel`, its manager should inherit `WarehouseModel.Manger` and set the type variable to a string with the model's name.
- [x] Write `objects: Manager = Manger()` below a custom manager.

If you're defining an abstract model with a custom manager:

- [x] Create a type variable lazily bound to the abstract model with naming convention `Any{model}`.
- [x] Add generic type parameter of type any model that inherits the abstract model on the manager.
- [x] Write `objects: Manager[t.Self] = Manger()` below a custom manager.

---

A model's manager should be defined within the model's class as `Manager`. If the model inherits `WarehouseModel`, the manager should inherit `WarehouseModel.Manager`, providing a string of the model's name as the type parameter to inform the manager of the type of model it will be managing. Below the manager's definition, create a class-level attribute on the model called `objects` which has its type set to `Manager` and it's value set to an instance of the `Manager` class.

```py
class Person(WarehouseModel):
  class Manager(WarehouseModel.Manager["Person"]): ...

  objects: Manager = Manager()
```

Note that Django requires the `User` model's manager to be defined globally (not locally nested within the `User` class). This is an exception and is required by Django so that it may auto-discover the location of the user-manager.

If you need to create an abstract model with a custom manager, add a generic type parameter to the manager which is bound to the manager's model. A type variable will need to be defined before the abstract model, following the naming convention `Any{model}`. However, to bind the type variable to the model before the model is defined, use a lazy binding by referencing the model's name as a string. Below the abstract model's manager, set the type of `objects` to be `Manager[t.Self]` so that the manager is managing the type of the inherited model (not the abstract model).

```py
import typing as t

AnyPerson = t.TypeVar("AnyPerson", bound="AbstractPerson")

class AbstractPerson(WarehouseModel):
  class Meta(TypedModelMeta):
    abstract = True

  class Manager(WarehouseModel.Manager[AnyPerson], t.Generic[AnyPerson]): ...

  objects: Manager[t.Self] = Manager() 

class Musician(AbstractPerson):
  class Manager(AbstractPerson.Manager["Musician"]): ...

  objects: Manager = Manager()
```

## Defining Constraints

TL;DR

- [x] Use constraint naming convention `{field}__{condition}`.
- [x] Use unit-test naming convention `test_constraint__{constraint_name}`.
- [x] Use CFL's assertion helper `assert_check_constraint`.

---

When defining constraints, the naming convention is `{field}__{condition}`.

```py
class Person(WarehouseModel):
  years_old = models.IntegerField()

  class Meta(TypedModelMeta):
    constraints = [
      models.CheckConstraint(
        check=models.Q(years_old__gte=18),
        name="years_old__gte__18"
      )
    ]
```

Test your custom constraint in `models/{model}_test.py`. Your test name should follow the naming convention `test_constraint__{constraint_name}`. The unit test should leverage CFL's assertion helper `assert_check_constraint`, which will check the constraint is enforced under the expected conditions.

```py
class TestPerson(ModelTestCase[Person]):
  def test_constraint__years_old__gte__18(self):
    with self.assert_check_constraint("years_old__gte__18"):
      Person.objects.create(years_old=17)
```

## Define Verbose Names

When defining a model, set its verbose names in its meta attributes.

```py
from django.utils.translation import gettext_lazy as _

class Person(WarehouseModel):
  class Meta(TypedModelMeta):
    verbose_name = _("person")
    verbose_name_plural = _("persons")
```

## QuerySets as Properties

TL;DR

- [x] Convert common query-sets filtered by model instance's attributes to properties.
- [x] Import models inside the property to avoid circular-imports.

---

If there are query-sets that are filtered by a model instance's attributes, create properties on the model's class that return the query-sets. This achieves a shorthand that makes the code base less repetitive and more readable. It's only worth doing this if the query-set is used in 2 or more locations in the code base.

```py
class Person(WarehouseModel):
  favorite_music_genre = models.TextField()
  
  @property
  def recommended_songs(self):
    """Songs recommended for this person based on their favorite music genre."""
    # pylint: disable-next=import-outside-toplevel
    from .song import Song

    return Song.objects.filter(genre=self.favorite_music_genre)
```

We import `Song` outside the top level to avoid circular-imports.

## Defining Settings

If a model has business logic that impacts its functionality based on custom conditions, add class-level settings on the model in all caps to configure the conditions.

For example, if the `Person` model has a property which checks if the person is too young:

```py
class Person(WarehouseModel):
  MIN_YEARS_OLD = 16

  years_old = models.IntegerField()

  @property
  def is_too_young(self):
    return self.years_old < self.MIN_YEARS_OLD 
```

This will also help to make tests more robust as values can be dynamically calculated.

```py
class TestPerson(ModelTestCase[Person]):
  def test_is_too_young(self):
    assert Person(years_old=Person.MIN_YEARS_OLD - 1).is_too_young
```
