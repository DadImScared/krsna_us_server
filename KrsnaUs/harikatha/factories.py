
import factory
import factory.fuzzy

from .models import User, Playlists, PlaylistItem, HarikathaCollection


class HarikathaCollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HarikathaCollection

    title = factory.Sequence(lambda n: 'title{}'.format(n))
    link = factory.Sequence(lambda n: 'link{}'.format(n))
    category = factory.fuzzy.FuzzyChoice(choices=['movie', 'song', 'harikatha', 'lecture'])


class PlaylistItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlaylistItem

    playlist = factory.SubFactory('harikatha.factories.PlaylistsFactory')
    collection_item = factory.SubFactory(HarikathaCollectionFactory)
    item_order = factory.Sequence(lambda n: n)


class PlaylistsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Playlists
        django_get_or_create = ('name', 'creator')

    name = factory.Sequence(lambda n: 'playlist{}'.format(n))
    creator = factory.SubFactory('harikatha.factories.UserFactory')

    @factory.post_generation
    def items(self, create, amount, **kwargs):
        if not create:
            return

        for n in range(0, amount if amount else 5):
            PlaylistItemFactory(playlist=self)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user{}'.format(n))
    email = factory.Sequence(lambda n: 'user{}@email.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True
    # playlists = factory.RelatedFactory('harikatha.factories.PlaylistsFactory', 'creator')

    @factory.post_generation
    def playlists(self, create, amount, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        for _ in range(0, amount if amount else 5):
            PlaylistsFactory(creator=self, items=kwargs.get('items', 5))
