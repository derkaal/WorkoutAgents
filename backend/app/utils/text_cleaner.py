import re

def clean_text_for_tts(text: str) -> str:
    """
    Removes common Markdown syntax from text to prepare it for Text-to-Speech (TTS).

    Args:
        text: The input string potentially containing Markdown.

    Returns:
        The cleaned string with Markdown removed.
    """
    # Remove bold (**text**) and italics (*text* or _text_)
    cleaned_text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # For **bold**
    cleaned_text = re.sub(r'\*([^\*]+)\*', r'\1', cleaned_text)  # For *italics*
    cleaned_text = re.sub(r'_([^_]+)_', r'\1', cleaned_text)  # For _italics_

    # Remove headers (# Header)
    cleaned_text = re.sub(r'#+\s*', '', cleaned_text)

    # Remove list markers (- item, * item, + item)
    cleaned_text = re.sub(r'^\s*[-*+]\s+', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove extra newlines that might result from stripping markdown
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text).strip()

    return cleaned_text