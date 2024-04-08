# Serializers

Below are the conventions we follow when serializing our data.

First, understand how to [serialize a Django model](https://www.django-rest-framework.org/api-guide/serializers/#modelserializer).

## Model Serializers

For each model, we create a file with the naming convention `{model}.py` in the directory `serializers`. Within a model's serializer-file, we create one or more serializers. It's advised to create one serializer per [model-view-set](./VIEWS.md#model-view-sets) action. Each model-serializer should inherit CFL's `ModelSerializer` by default and set the type parameter to the model being serialized.

```py
# serializers/person.py
from codeforlife.serializers import ModelSerializer

from ..models import Person

class CreatePersonSerializer(ModelSerializer[Person]):
  class Meta:
    model = Person

class UpdatePersonSerializer(ModelSerializer[Person]):
  class Meta:
    model = Person
```

To avoid repetitively setting the model being serialized to `Person`, a base serializer may be created with the naming convention `Base{model}Serializer`.

```py
# serializers/person.py
from codeforlife.serializers import ModelSerializer

from ..models import Person

class BasePersonSerializer(ModelSerializer[Person]):
  class Meta:
    model = Person

class CreatePersonSerializer(BasePersonSerializer): ...

class UpdatePersonSerializer(BasePersonSerializer): ...
```

All serializers should be imported into `serializers/__init__.py` to support importing multiple serializers from `serializers`.

```py
# serializers/__init__.py
from .person import CreatePersonSerializer, UpdatePersonSerializer
```

Any custom logic defined in a model-serializer-file should be tested in the directory `serializers`, where each model has its own serializer-test-file following the naming convention `{model}_test.py`. Model-serializer-test-cases should inherit CFL's `ModelSerializerTestCase`, set the type parameter to be the model being serialized and set `model_serializer_class` to the model-serializer being tested. The name of the model-serializer-test-case should follow the convention `Test{model}Serializer`.

```py
# serializers/person_test.py
from codeforlife.tests import ModelSerializerTestCase

from ...models import Person
from ...serializers.person import PersonSerializer

class TestPersonSerializer(ModelSerializerTestCase[Person]):
  model_serializer_class = PersonSerializer
```

## Model List Serializers

When defining model-list-serializers, follow the naming convention `{model}ListSerializer`. Model-list-serializers should inherit CFL's `ModelListSerializer` by default to support bulk-creating and bulk-updating model instances.

```py
from codeforlife.serializers import ModelListSerializer

from ..models import Person

class PersonListSerializer(ModelListSerializer[Person]): ...
```

When overriding `validate(self, attrs)`, *always* call `super().validate(attrs)` first before implementing any additional validations. This is necessary to ensure the data is valid before bulk-creating or bulk-updating.

```py
class PersonListSerializer(ModelListSerializer[Person]):
  def validate(self, attrs):
    super().validate(attrs)
```

When overriding `update(self, instance, validated_data)`, both `instance` and `validated_data` are of equal length and sorted in the correct order. Therefore, to get the data per model, use `zip` on `instance` and `validated_data`.

```py
class PersonListSerializer(ModelListSerializer[Person]):
  def update(self, instance, validated_data):
    for person, data in zip(instance, validated_data): ...
```

## Validation Errors

When defining validation errors, always set the `code` of the validation error so that it may be asserted in a test. Error codes **must** always be unique per validation function so that they may be individually asserted in tests.

```py
class PersonSerializer(ModelSerializer[Person]):
  years_old = serializers.IntegerField()
  country = serializers.CharField()

  def validate_years_old(self, value: int):
    if value < 18:
      raise serializers.ValidationError(
        "You are too young.",
        code="too_young",
      )
  
  def validate(self, attrs):
    if attrs["country"] == "GB" and attrs["years_old"] < 16:
      raise serializers.ValidationError(
        "A person in GB must be at least 16 years old.",
        code="gb_too_young",
      )
```

When testing validation errors, the `error_code` that is expected to be raised must be provided. When testing the validations of a field, the test must follow the naming convention `test_validate_{field}__{validation_error_code}` and use CFL's `assert_validate_field` helper. When testing general validations, the test must follow the naming convention `test_validate__{validation_error_code}` and use CFL's `assert_validate` helper.

```py
class TestPersonSerializer(ModelSerializerTestCase[Person]):
  model_serializer_class = PersonSerializer

  def test_validate_years_old__too_young(self):
    """A person must be at least 18."""
    self.assert_validate_field(
      name="years_old",
      value=17,
      error_code="too_young",
    )
  
  def test_validate__gb_too_young(self):
    """A person in GB must be at least 16."""
    self.assert_validate(
      attrs={"country": "GB", "years_old": 16},
      error_code="gb_too_young",
    )
```

## Testing create() and update()

If `create(self, validated_data)` was overridden in a model-serializer, a test named `test_create` will need to be created and use CFL's `assert_create` helper. Likewise, if `update(self, instance, validated_data)` was overridden in a model-serializer, a test named `test_update` will need to be created and use CFL's `assert_update` helper.

```py
class PersonSerializer(ModelSerializer[Person]):
  years_old = serializers.IntegerField()

  def create(self, validated_data):
    return Person.objects.create(**validated_data, created_at=timezone.now())
  
  def update(self, instance, validated_data):
    instance.years_old = validated_data["years_old"]
    instance.last_updated_at = timezone.now()
    instance.save(update_fields=["years_old", "last_updated_at"])
    
    return instance
```

```py
class TestPersonSerializer(ModelSerializerTestCase[Person]):
  model_serializer_class = PersonSerializer

  def test_create(self):
    """A person is successfully created."""
    self.assert_create(validated_data={"years_old": 18})
  
  def test_update(self):
    """A person is successfully updated."""
    self.assert_update(
      instance=Person.objects.get(pk=1),
      validated_data={"country": "GB", "years_old": 15},
    )
```

If `create(self, validated_data)` was overridden in a model-list-serializer, a test named `test_create_many` will need to be created and use CFL's `assert_create_many` helper. Likewise, if `update(self, instance, validated_data)` was overridden in a model-list-serializer, a test named `test_update_many` will need to be created and use CFL's `assert_update_many` helper.

```py
class PersonListSerializer(ModelListSerializer[Person]):
  def create(self, validated_data):
    return Person.objects.bulk_create([
      Person(**person_fields, created_at=timezone.now())
      for person_fields in validated_data
    ])
  
  def update(self, instance, validated_data):
    for person, data in zip(instance, validated_data):
      person.years_old = validated_data["years_old"]
      person.last_updated_at = timezone.now()
      person.save(update_fields=["years_old", "last_updated_at"])
      
    return instance

class PersonSerializer(ModelSerializer[Person]):
  years_old = serializers.IntegerField()

  class Meta:
    model = Person
    list_serializer_class = PersonListSerializer
```

```py
class TestPersonSerializer(ModelSerializerTestCase[Person]):
  model_serializer_class = PersonSerializer

  def test_create_many(self):
    """Many people are successfully created at once."""
    self.assert_create_many(
      validated_data=[{"years_old": 18}, {"years_old": 25}]
    )
  
  def test_update_many(self):
    """Many people are successfully updated at once."""
    self.assert_update_many(
      instance=[Person.objects.get(pk=1), Person.objects.get(pk=2)],
      validated_data=[{"years_old": 67}, {"years_old": 49}],
    )
```

## Testing to_representation()

If `to_representation(self, instance)` was overridden in a model-serializer, a test named `test_to_representation` will need to be created and use CFL's `assert_to_representation` helper.

```py
class PersonSerializer(ModelSerializer[Person]):
  def to_representation(self, instance):
    representation = super().to_representation()
    representation["is_too_young"] = instance.years_old < 18

    return representation
```

```py
class TestPersonSerializer(ModelSerializerTestCase[Person]):
  model_serializer_class = PersonSerializer

  def test_to_representation(self):
    """A data-field designating if a person is too young is included."""
    person = Person.objects.filter(age=17).first()
    assert person is not None

    self.assert_to_representation(
      instance=person,
      new_data={"is_too_young": True},
    )
```
