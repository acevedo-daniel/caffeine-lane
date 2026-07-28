import factory
from django.utils import timezone

from apps.accounts.models import User
from apps.posts.models import Category, Post


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda number: f"user-{number}")
    email = factory.LazyAttribute(lambda instance: f"{instance.username}@example.com")

    @factory.post_generation
    def password(instance, create, extracted, **kwargs):
        value = extracted or "test-password"
        instance.set_password(value)
        if create:
            instance.save(update_fields=["password"])


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda number: f"Category {number}")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        skip_postgeneration_save = True

    title = factory.Sequence(lambda number: f"Post {number}")
    content = "Factory-generated legacy content."
    author = factory.SubFactory(UserFactory)
    status = "published"
    published_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def categories(instance, create, extracted, **kwargs):
        if create:
            instance.categories.add(extracted or CategoryFactory())
