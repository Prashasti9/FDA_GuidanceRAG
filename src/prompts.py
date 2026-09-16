import yaml
import pathlib

PROMPTS_DIR = pathlib.Path("prompts")


def load_prompt(version: str) -> dict:
    """Load a prompt template by version string, e.g. 'v1'."""
    path = PROMPTS_DIR / f"answer_{version}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def format_prompt(version: str, question: str, chunks: list) -> tuple[str, str]:
    """Returns (system_prompt_filled, prompt_version) ready to send to the model."""
    template = load_prompt(version)

    context_str = "\n\n".join(
        f"[{i+1}] (Source: {c.source}, Page: {c.page}, Section: {c.section})\n{c.text}"
        for i, c in enumerate(chunks)
    )

    filled = template["system_prompt"].format(context=context_str, question=question)
    return filled, template["version"]
