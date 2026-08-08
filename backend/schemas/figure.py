from dataclasses import dataclass


@dataclass
class FigureInfo:

    session_id: int

    paper_name: str

    page_number: int

    figure_number: str | None

    figure_caption: str | None

    image_path: str