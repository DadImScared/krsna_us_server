
import django
import os
import sys
sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KrsnaUs.settings")
django.setup()

from harikatha import search


if __name__ == '__main__':
    search.bulk_indexing()
