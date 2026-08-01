def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Simple sliding-window character chunker with overlap, splitting on
    paragraph/sentence boundaries where possible.
    """
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            search_start = max(start, end - 200)
            boundary = text.rfind("\n", search_start, end)
            if boundary == -1 or boundary <= search_start:
                boundary = text.rfind(". ", search_start, end)
            if boundary != -1 and boundary > search_start:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks
