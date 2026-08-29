from apps.api.providers.analytics.base import AnalyticsProvider


class SnowflakeAnalytics(AnalyticsProvider):

    async def record(self, event):

        # send event to Snowflake
        await insert_into_snowflake(event)