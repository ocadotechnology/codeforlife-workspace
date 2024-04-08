# Views

Below are the conventions we follow when viewing our data.

First, understand how to [view a Django model](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset).

## Model View Sets

For each model, we create a file with the naming convention `{model}.py` in the directory `views`. Within a model's view-file, we create one view-set following the naming convention `{model}ViewSet`. Each model-view-set should inherit CFL's `ModelViewSet` by default and set the type parameter to the model being viewed.

```py
# views/person.py
from codeforlife.views import ModelViewSet

from ..models import Person

class PersonViewSet(ModelViewSet[Person]): ...
```

All views should be imported into `views/__init__.py` to support importing multiple views from `views`.

```py
# views/__init__.py
from .person import PersonViewSet
```

Any custom logic defined in a model-view-file should be tested in the directory `views`, where each model has its own view-test-file following the naming convention `{model}_test.py`. Model-view-set-test-cases should inherit CFL's `ModelViewSetTestCase`, set the type parameter to be the model being viewed, set `model_view_set_class` to the model-view-set being tested and set `basename` to the basename used to register the model-view-set in the urls. The name of the model-view-set-test-case should follow the convention `Test{model}ViewSet`.

```py
# views/person_test.py
from codeforlife.tests import ModelViewSetTestCase

from ...models import Person
from ...views import PersonViewSet

class TestPersonViewSet(ModelViewSetTestCase[Person]):
  model_view_set_class = PersonViewSet
  basename = "person"
```

## Register URLs

Each model-view-set needs to be registered in `urls.py` using DRF's `DefaultRouter`. Each registration needs to set `prefix` to be the plural name of the model with kebab-casing, `viewset` to be the model-view-set being registered and `basename` to be the singular of the singular name of the model with kebab-casing.

```py
# urls.py
from rest_framework.routers import DefaultRouter

from .views import PersonViewSet

router = DefaultRouter()
router.register(
    prefix="persons",
    viewset=PersonViewSet,
    basename="person",
)

urlpatterns = router.urls
```

If a model has a foreign key to another model, it's also acceptable to set `prefix` to be a subpath of the related model, where each model's name is plural with kebab casing.

```py
from .views import PartyInvitationViewSet, VipPartyInvitationViewSet

router.register(
    prefix="parties/invitations",
    viewset=PartyInvitationViewSet,
    basename="party-invitation",
)
# in practice, `is_vip` would likely be a field of `PartyInvitationViewSet` but
# this example is purely to demonstrate the naming convention of `prefix`.
router.register(
    prefix="parties/vip-invitations",
    viewset=VipPartyInvitationViewSet,
    basename="vip-party-invitation",
)
```

## Permissions

Permissions must at the very least be set per action in `get_permissions`, but further conditions can be specified. All permission must be imported from CFL's package to support unit testing.

```py
from codeforlife.permissions import AllowNone
from codeforlife.user.permissions import IsTeacher

class SchoolViewSet(ModelViewSet[School]):
  def get_permissions(self):
    if self.action == "list":
      return [AllowNone()]
    if self.action == "destroy":
      return [IsTeacher(is_admin=True)]
    
    return [IsTeacher(in_school=True)]
```

If `get_permissions` is overriden, a test will need to be created for each action the model-view-set provides where each test follows the naming convention `test_get_permissions__{action}`. Each test should use CFL's `assert_get_permissions` helper.

```py
from codeforlife.permissions import AllowNone
from codeforlife.user.permissions import IsTeacher

class TestSchoolViewSet(ModelViewSetTestCase[School]):
  def test_get_permissions__list(self):
    """No one is allowed to list schools."""
    self.assert_get_permissions(
      permissions=[AllowNone()],
      action="list",
    )

  def test_get_permissions__destroy(self):
    """Only admin teachers can destroy schools."""
    self.assert_get_permissions(
      permissions=[IsTeacher(is_admin=True)],
      action="destroy",
    )

  def test_get_permissions__retrieve(self):
    """Only school teachers can retrieve schools."""
    self.assert_get_permissions(
      permissions=[IsTeacher(in_school=True)],
      action="retrieve",
    )
  
  ...
```

### Limiting Default Actions

If any of a model's [default actions](https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions) should not be allowed, they can be disallowed in one of 2 ways.

The first is by excluding an action's HTTP method from `http_method_names`. The is the preferred way if no action with that HTTP method should be allowed.

The second is to not permit some or all users to trigger the action. The is the preferred way if only some actions for a HTTP should be allowed.

```py
class PersonViewSet(ModelViewSet[Person]):
  http_method_names = ["get"]

  def get_permissions(self):
    if self.action == "list":
      return [AllowNone()]
    
    return [IsAuthenticated()]
```

In the above example, actions that do not use HTTP GET are not allowed (e.g. The destroy action which uses HTTP DELETE is not allowed). Futhermore, of the 2 actions which use HTTP GET: list and retrieve, list is not allowed and only authenticated users are allowed to retrieve.

## Custom Actions

If a custom action needs to be created for a model-view-set, use CFL's `action` decorator. A custom action should set `detail` and `methods`.

```py
from codeforlife.views import ModelViewSet, action

class PersonViewSet(ModelViewSet[Person]):
  @action(detail=True, methods=["post"])
  def send_reset_password_email(self, pk: str): ...
```

## Testing Actions

Each action provided by a model-view-set should have one test case that calls the action as it is intended to be called. Normally, unit tests can be said to test the "unhappy scenarios" - where we are asserting that the bad scenarios we are expecting to encounter are handled as expected. However, we will also test the "happy scenario" of each action to assert that the action does indeed work.

CFL has provided client-helpers to call and assert each of the default actions. Each action-test should follow the naming convention `test_{action}`.

```py
class TestPersonViewSet(ModelViewSetTestCase[Person]):
  def test_create(self):
    """Successfully creates a person."""
    self.client.create(
      data={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@codeforlife.education",
      },
    )
```

## Custom Update or Bulk-Update Actions

If a custom update or bulk-update action needs to be created for a model-view-set, use CFL's `ModelViewSet.update_action` or `ModelViewSet.bulk_update_action` helpers and pass the name of the action as the first argument. As these actions require a serializer to be provided, you'll also need to override `get_serializer_class`.

**NOTE:** Update actions use HTTP PUT and so it needs to be added to `http_method_names`.

```py
class PersonViewSet(ModelViewSet[Person]):
  http_method_names = ["put"]

  def get_serializer_class(self):
    if action == "reset_password":
      return ResetPersonPasswordSerializer
    if action == "block_login":
      return BlockPersonLoginSerializer
    
    return PersonSerializer

  reset_password = ModelViewSet.update_action("reset_password")
  block_login = ModelViewSet.bulk_update_action("block_login")
```

To test the "[happy scenarios](#testing-actions)" of each update action, use CFL's client helpers `update` or `bulk_update`.

```py
class TestPersonViewSet(ModelViewSetTestCase[Person]):
  def test_reset_password(self):
    """Successfully resets a person's password."""
    self.client.update(
      model=person,
      data={"password": "example password"},
      action="reset_password",
    )

  def test_block_login(self):
    """Successfully block the specified persons from logging in."""
    self.client.bulk_update(
      models=[person1, person2],
      data=[{}, {}],  # no additional data required
      action="block_login",
    )
```

## Testing get_queryset()

If you are overriding a model-view-set's `get_queryset` callback, a test will need to be created for each action at the very least where each test follows naming convention `test_get_queryset__{action}`. Each test will need to use CFL's `assert_get_queryset` helper. Additional test dimensions can be specified if other factors affect a queryset.

```py
class CarViewSet(ModelViewSet[Car]):
  def get_queryset(self):
    queryset = Car.objects.filter(is_insured=True)
    if action == "drive":
      return queryset.filter(owner=self.request.user)
    if action == "list":
      return queryset | queryset.filter(is_insured=False)

    return queryset
```

In the above example, the default queryset is all insured cars. For the drive action, only insured owners can drive their cars. For the list action, insured or uninsured cars can be listed.

```py
class TestCarViewSet(ModelViewSetTestCase[Car]):
  def test_get_queryset__drive(self):
    """Only cars owned by the requesting user can be driven."""
    self.assert_get_queryset(
      values=Car.objects.filter(is_insured=True, owner=user),
      action="drive",
      request=self.client.request_factory.post(user=user),
    )

  def test_get_queryset__list(self):
    """All cars can be listed."""
    self.assert_get_queryset(
      values=Car.objects.all(),
      action="list",
    )
  
  def test_get_queryset__partial_update(self):
    """Only insured cars can be partially updated."""
    self.assert_get_queryset(
      values=Car.objects.filter(is_insured=True),
      action="partial_update",
    )

  ...
```

## Testing get_serializer_class()

If you are overriding a model-view-set's `get_serializer_class` callback, a test will need to be created for each action at the very least where each test follows naming convention `test_get_serializer_class__{action}`. Each test will need to use CFL's `assert_get_serializer_class` helper.

```py
from ..serializers.person import (
  CreatePersonSerializer,
  ListPersonSerializer,
  PersonSerializer
)

class PersonViewSet(ModelViewSet[Person]):
  def get_serializer_class(self):
    if self.action == "create":
      return CreatePersonSerializer
    if self.action == "list":
      return ListPersonSerializer

    return PersonSerializer
```

```py
from ...serializers.person import (
  CreatePersonSerializer,
  ListPersonSerializer,
  PersonSerializer
)

class TestPersonViewSet(ModelViewSetTestCase[Person]):
  def test_get_serializer_class__create(self):
    """Creating a person has a dedicated serializer."""
    self.assert_get_serializer_class(
      serializer_class=CreatePersonSerializer,
      action="create",
    )

  def test_get_serializer_class__list(self):
    """Listing persons has a dedicated serializer."""
    self.assert_get_serializer_class(
      serializer_class=ListPersonSerializer,
      action="list",
    )

  def test_get_serializer_class__partial_update(self):
    """Partially updating a person uses the general serializer."""
    self.assert_get_serializer_class(
      serializer_class=PersonSerializer,
      action="partial_update",
    )

  ...
```

## Testing get_serializer_context()

If you are overriding a model-view-set's `get_serializer_context` callback, only the actions that have additional context will need to have a test created. The test should follow the naming convention `test_get_serializer_context__{action}`. Each test will need to use CFL's `assert_get_serializer_context` helper.

```py
class PersonViewSet(ModelViewSet[Person]):
  def get_serializer_context(self):
    context = super().get_serializer_context()
    if self.action == "create":
      context["favorite_color"] = "red" 
    
    return context
```

```py
class TestPersonViewSet(ModelViewSetTestCase[Person]):
  def test_get_serializer_context__create(self):
    """Includes the person's favorite color."""
    self.assert_get_serializer_context(
      serializer_context={"favorite_color": "red"},
      action="create",
    )
```
