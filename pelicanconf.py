#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Joris Van den Bossche'
SITENAME = 'Joris Van den Bossche'
SITEURL = 'https://jorisvandenbossche.github.io'

TIMEZONE = 'Europe/Brussels'
DEFAULT_LANG = 'en'

PATH = 'content'

STATIC_PATHS = [
    "images/",
    "figures/",
    "downloads/",
]


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Set the article URL
ARTICLE_URL = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

# PLugins
PLUGIN_PATHS = ['./plugins', './plugins/pelican-plugins']
PLUGINS = [
    'summary', # auto-summarizing articles
    'ipynb.liquid',  # for embedding notebooks
]


# Theme
THEME = "pelican-themes/pelican-sober"

PELICAN_SOBER_ABOUT = "Pandas core developer. Working at the Paris-Saclay Center for Data Science"

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('github', 'https://github.com/jorisvandenbossche/'),
          ('twitter', 'https://twitter.com/jorisvdbossche'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

LOAD_CONTENT_CACHE = False
