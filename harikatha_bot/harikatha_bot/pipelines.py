# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem
from django.db import IntegrityError


class HarikathaBotPipeline(object):
    """A pipeline to save items to the database"""
    def process_item(self, item, spider):
        try:
            item.save()
        except IntegrityError:
            raise DropItem("Duplicate item found {}".format(item))
        return item


class BhagavatPatrikaPipeline(object):
    """Adds year and issue to the HarikathaBotItem"""
    def process_item(self, item, spider):
        """Return item"""
        clean_link = item['link'].rsplit('/', 1)[0].rsplit('/', 1)[1]
        # Extract year from link
        year = ''
        # Extract issue from link
        issue = ""

        issue_all = re.compile(r'issue-?[a-zA-z]+')
        multiple_issues = re.compile(r'issue-[0-9]+-?a?n?d?-?-[0-9]+')
        one_issue = re.compile(r'issue-[0-9]+$')
        year = re.search(r'year-[0-9]{4}', clean_link).group(0).strip().split('-')[-1]
        item['year'] = str(year)

        # if issue is "all" and not a traditional issue like 1, 2 ,3 etc
        if issue_all.search(clean_link):
            issue = issue_all.search(clean_link).group(0).strip().split('-')
            issue = issue[-1]
            item['issue'] = str(issue)
        # sometimes multiple issues exist as one link. Separate them and save as two items
        if multiple_issues.search(clean_link):
            issue = multiple_issues.search(clean_link).group(0).strip().split('-')
            issue = ",".join([x for x in issue if x.isdigit()]).split(',')
            second_item = item.copy()
            item['issue'] = str(issue[0])
            second_item['issue'] = str(issue[1])
            try:
                second_item.save()
            except IntegrityError:
                pass
        # one issue like expected
        if one_issue.search(clean_link):
            issue = one_issue.search(clean_link).group(0).strip().split('-')
            issue = issue[-1]
            item['issue'] = str(issue)
        return item
