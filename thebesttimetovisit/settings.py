# Scrapy settings for Scrapy_LonelyPlanet project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawl.settings")

BOT_NAME = 'thebesttimetovisit'
#
SPIDER_MODULES = ['thebesttimetovisit.spiders']
NEWSPIDER_MODULE = 'thebesttimetovisit.spiders'
ITEM_PIPELINES = {
    'thebesttimetovisit.pipelines.TheBestTimeToVisitPipeline': 1
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Scrapy_LonelyPlanet (+http://www.yourdomain.com)'
