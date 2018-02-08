
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
    language = models.CharField(null=True, max_length=255)
    #: year. required when choice is bhagavatpatrika
    year = models.CharField(null=True, max_length=255)
    #: issue. required when choice is bhagavatpatrika
    issue = models.CharField(null=True, max_length=255)
    #: directory. required when choice is song general used when at highest directory
    directory = models.CharField(null=True, max_length=255)

    class Meta:
        unique_together = (("title", "link", 'issue'),)
        ordering = ['category']

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
