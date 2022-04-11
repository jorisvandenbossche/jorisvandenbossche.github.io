AUTHOR = 'Joris Van den Bossche'
SITENAME = 'Joris Van den Bossche'
SITEURL = ''

TIMEZONE = 'Europe/Brussels'
DEFAULT_LANG = 'en'

PATH = 'content'

STATIC_PATHS = [
    "images/",
    "figures/",
    "downloads/",
]

# Set the article URL
ARTICLE_URL = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Plugins
PLUGIN_PATHS = ['./plugins', './plugins/pelican-plugins']
PLUGINS = [
    'summary', # auto-summarizing articles
    'ipynb.liquid',  # for embedding notebooks
]

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {'permalink': True},
    },
    'output_format': 'html5',
}

# Theme
#THEME = "pelican-themes/pelican-hss"
THEME = './theme'

ABOUT_PAGE = '/pages/about.html'
TWITTER_USERNAME = 'jorisvdbossche'
GITHUB_USERNAME = 'jorisvandenbossche'
STACKOVERFLOW_ADDRESS = 'https://stackoverflow.com/users/653364/joris'
AUTHOR_BLOG = 'http://jorisvandenbossche.github.io'

# Blogroll
# LINKS = (('Pelican', 'https://getpelican.com/'),
#          ('Python.org', 'https://www.python.org/'),
#          ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
#          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('github', 'https://github.com/jorisvandenbossche/'),
          ('twitter', 'https://twitter.com/jorisvdbossche'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True