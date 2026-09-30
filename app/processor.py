def clean_text(text):
    """
    Clean and normalize extracted lecture transcript text.
    """

    cleaned_lines = []

    for line in text.splitlines():

        # Remove leading/trailing whitespace
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)