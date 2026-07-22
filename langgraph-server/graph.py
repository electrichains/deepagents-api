import os

from deepagents import create_deep_agent


def _build_model():
    model = os.environ.get("DEEPAGENTS_MODEL", "openai:openai/gpt-4o")
    openai_base_url = os.environ.get("OPENAI_BASE_URL")
    if openai_base_url:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model.removeprefix("openai:"),
            base_url=openai_base_url,
        )
    return model


agent = create_deep_agent(model=_build_model())
