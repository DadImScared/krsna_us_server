
import re

pattern = r'(?<!\d)\d{2} (\d{2}\s?)* (\d{4}|\d{2})(?!\d)'


def fix_date(year):
    """Accept two digit year as string and return four digit year as string

    :param str year: Two digit year. example '08'
    :return: Four digit year. example '2008
    """
    if len(year) > 2:
        return year
    try:
        int_year = int(year)
    except ValueError as e:
        raise e
    else:
        if int_year == 20:
            return '{}{}'.format(year, 00)
        elif int_year < 80:
            return '{}{}'.format(20, year)
        else:
            return '{}{}'.format(19, year)


def format_title(title):
    """Accepts a title from the movie spider and returns a title

    :param str title: A string that has a date formatted as mm dd yy or mm dd yyyy
    :return: A new string with date formatted as yyyy mm dd
    """
    result = re.search(pattern, title)
    if not result:
        return title
    before, after = result.span()
    fixed_date = result.group().split(' ')
    fixed_date = [fix_date(fixed_date[-1])] + fixed_date[:-1]
    if before:
        new_title = '{}{} {}'.format(title[:before], ' '.join(fixed_date), title[after+1:])
    else:
        new_title = '{} {}'.format(' '.join(fixed_date), title[after+1:])
    new_title = new_title.strip()
    return new_title
