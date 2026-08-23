from typing import List, Optional
from openai import OpenAI
from src.config import config

class LLMInterface:
    """Handles communication with any LLM via OpenAI-compatible endpoint."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.default_api_key = api_key or config.llm_api_key
        self.base_url = config.llm_base_url

    def _get_client(self, api_key: Optional[str] = None) -> OpenAI:
        key = api_key or self.default_api_key
        return OpenAI(
            api_key=key,
            base_url=self.base_url
        )

    def generate_answer(
        self, 
        query: str, 
        context_chunks: List[str], 
        api_key: Optional[str] = None
    ) -> str:
        """
        Generates an answer strictly grounded in context chunks.
        Accepts an optional runtime API key.
        """
        active_key = api_key or self.default_api_key
        if not active_key:
            return "❌ Error: No API key provided. Please enter your API key in the sidebar."

        if not context_chunks:
            return "I don't have any context to answer this question."

        context_string = "\n\n---\n\n".join(context_chunks)

        system_prompt = (
            "You are an expert technical assistant. Answer the user's question "
            "based ONLY on the provided context below. If the answer is not contained "
            "in the context, state: 'I do not know based on the provided documents.' "
            "Do not use outside knowledge.\n\n"
            f"CONTEXT:\n{context_string}"
        )

        try:
            client = self._get_client(active_key)
            response = client.chat.completions.create(
                model=config.llm_model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error communicating with the LLM: {str(e)}"