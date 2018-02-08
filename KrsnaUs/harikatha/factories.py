
import factory

from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user{}'.format(n))
    email = factory.Sequence(lambda n: 'user{}@email.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True
