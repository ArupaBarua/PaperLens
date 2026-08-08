from sqlalchemy.orm import Session

from backend.database.crud import get_figure_by_number, get_figure_by_caption
from backend.services.figure_ref_extractor import FigureReferenceExtractor, FigureReferenceType
from backend.services.figure_analyzer import FigureAnalyzer
from backend.services.retriever import Retriever
from backend.services.chroma_manager import ChromaManager
from backend.services.context_optimizer import optimize_context

from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

ref_extractor = FigureReferenceExtractor()
fig_analyzer = FigureAnalyzer()
chroma_maanger = ChromaManager()
retriever = Retriever(chroma_manager=chroma_maanger)

def answer(
    db: Session,
    session_id: int,
    query: str
) -> str:
    """
    Answers a user's question about a figure in the paper.
    """

    reference = ref_extractor.extract(query=query)

    if reference is None:
        logger.info("No figure reference found.")

        return (
            "I couldn't determine which figure you are referring to"
        )
    reference_type, reference_value = reference

    if reference_type == FigureReferenceType.NUMBER:
        figure = get_figure_by_number(
            db=db,
            session_id=session_id,
            figure_number=reference_value
        )

    else:
        figure = get_figure_by_caption(
            db=db,
            session_id=session_id,
            caption=reference_value
        )

    if figure is None:

        logger.info(f"Figure '{reference_value}' was not found")

        return "I couldn't find the requested figure in the uploaded paper."
    
    logger.info(
        f"Found Figure {figure.figure_number} "
        f"for session {session_id}."
    )

    documents = retriever.retrieve(query=query, session_id=session_id)

    documents = optimize_context(documents=documents)
    
    answer = fig_analyzer.analyze(figure=figure, question=query, documents=documents)

    logger.info("Figure question answered successfully.")

    return answer
