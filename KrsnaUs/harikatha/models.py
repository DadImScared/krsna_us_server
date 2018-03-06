
import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from .search import HarikathaIndex

# Create your models here.


class User(AbstractUser):
    pass


class HarikathaCollection(models.Model):
    #: tuple of choices, required for a collection entry
    CATEGORY_CHOICES = (
        ("harikatha", "Harikatha"),
        ("harmonistmonthly", "Harmonist Monthly"),
        ("harmonistmagazine", "Harmonist Magazine"),
        ("lecture", "Lecture"),
        ("movie", "Movie"),
        ("song", "Song"),
        ("bhagavatpatrika", "Bhagavat Patrika"),
        ('book', 'Book')
    )
    item_id = models.UUIDField(default=uuid.uuid4, unique=True)
    #: title of collection item. required
    title = models.CharField(max_length=255)
    #: link to collection item. required
    #: various sources: youtube, soundcloud, purebhakti.com, etc
    link = models.URLField()
    #: One of CATEGORY_CHOICES. required
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=255)
    #: indexed. Used to track if an items content has been indexed for searching
    indexed = models.BooleanField(default=False)
    #: language of book. required when choice is book
    language = models.CharField(null=True, blank=True, max_length=255)
    #: year. required when choice is bhagavatpatrika
    year = models.CharField(null=True, blank=True, max_length=255)
    #: issue. required when choice is bhagavatpatrika
    issue = models.CharField(null=True, blank=True, max_length=255)
    #: directory. required when choice is song general used when at highest directory
    directory = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        unique_together = (("title", "link", 'issue'), ('title', 'link'))
        ordering = ['category']
        permissions = (
            ('write_book', 'Write books'),
            ('write_movie', 'Write movies'),
            ('write_bhagavatpatrika', 'Write Bhagavat Patrika'),
            ('write_harmonistmonthly', 'Write Harmonist Monthly'),
            ('write_harmonistmagazine', 'Write Harmonist Magazine'),
            ('write_harikatha', 'Write Hari Katha'),
            ('write_song', 'Write songs'),
            ('write_lecture', 'Write lectures')
        )

    def indexing(self):
        """Index the record to elastic search"""
        obj = HarikathaIndex(
            meta={"id": self.item_id},
            title=self.title,
            title_suggest={
                "input": self.title,
                "contexts": {
                    "category_type": self.category
                }
            },
            link=self.link,
            phrase_suggest=self.title,
            language=self.language,
            category=self.category,
            year=self.year,
            issue=self.issue,
            directory=self.directory,
        )
        obj.save()
        return obj.to_dict(include_meta=True)


class Playlists(models.Model):
    creator = models.ForeignKey(User, related_name='playlists', on_delete=models.CASCADE)
    name = models.TextField()
    playlist_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlists, related_name='items')
    collection_item = models.ForeignKey(HarikathaCollection)
    item_id = models.UUIDField(default=uuid.uuid4, unique=True)
    item_order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_order']
        unique_together = ('playlist', 'collection_item')
