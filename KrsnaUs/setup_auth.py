
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KrsnaUs.settings")
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


def create_site():
    site_domain = os.environ['SITE_DOMAIN']
    site_name = os.environ['SITE_NAME']
    site = Site.objects.get(id=1)
    if site.domain != site_domain:
        site.domain = site_domain
        site.name = site_name
        site.save()
    return site


def create_social_apps(site):
    """Registers all social apps to site

    :param site: Site object to attach social apps to
    :return: None
    """
    social_apps = os.environ['SOCIAL_APPS'].split(',')
    for app in social_apps:
        uppercase_app = app.upper()
        title_app = app.title()
        try:
            client_id = os.environ['{}_CLIENT'.format(uppercase_app)]
            client_secret = os.environ['{}_SECRET'.format(uppercase_app)]
        except KeyError:
            raise ValueError('Missing client id or secret for {}'.format(title_app))
        else:
            social_app, created = SocialApp.objects.get_or_create(
                provider=app,
                name=title_app,
                client_id=client_id,
                secret=client_secret
            )
            if created:
                social_app.sites.add(site)


def main():
    site = create_site()
    create_social_apps(site)


if __name__ == '__main__':
    main()
