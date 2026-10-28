BOT_NAME = "technology_jobs"
SPIDER_MODULES = ["jobboard.crawler.spiders"]
NEWSPIDER_MODULE = "jobboard.crawler.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
RETRY_ENABLED = True
RETRY_TIMES = 3
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
USER_AGENT = "TechnologyJobsAggregator/0.1 (+public-job-indexer)"
LOG_LEVEL = "INFO"

ITEM_PIPELINES = {
    "jobboard.crawler.pipelines.ValidationPipeline": 100,
    "jobboard.crawler.pipelines.DatabasePipeline": 300,
}

FEED_EXPORT_ENCODING = "utf-8"
