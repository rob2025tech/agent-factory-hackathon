from apps.api.providers.analytics.base import AnalyticsProvider


class LocalAnalytics(AnalyticsProvider):

    async def record(self, event):

        with open("analytics.json", "a") as f:
            f.write(str(event))