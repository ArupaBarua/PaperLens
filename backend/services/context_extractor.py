import re

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


TOP_LEVEL_HEADING_PATTERN = re.compile(
    r"""
    ^
    (
        Abstract |
        Introduction |
        Background |
        Preliminaries |
        Related\ Work |
        Literature\ Review |
        Methodology |
        Methods |
        Materials\ and\ Methods |
        Experimental\ Setup |
        Experiments |
        Evaluation |
        Results |
        Discussion |
        Limitations |
        Future\ Work |
        Conclusion |
        Conclusions |
        References |
        Bibliography |
        Acknowledg(?:e)?ments? |
        Appendix |
        \d+\.?\s+.* |
        [IVXLCDM]+\.?\s+.*
    )
    $
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE
)


def extract_sections(text: str) -> dict[str, str]:
    """
    Splits a research paper into top-level sections.

    Subsections remain inside their parent section.
    """

    matches = list(TOP_LEVEL_HEADING_PATTERN.finditer(text))

    if not matches:
        logger.warning("No top-level headings found.")
        return {
            "Full Text": text.strip()
        }

    sections = {}

    for i, match in enumerate(matches):

        heading = match.group(1).strip()

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        sections[heading] = text[start:end].strip()

    logger.info(f"Extracted {len(sections)} top-level sections.")

    return sections