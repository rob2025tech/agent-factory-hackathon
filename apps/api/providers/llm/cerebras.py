from .base import LLMProvider


class CerebrasProvider(LLMProvider):

    async def execute(self,prompt):

        # call Cerebras API

        return response