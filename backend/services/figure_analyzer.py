from langchain_core.documents import Document
from backend.database.models import Figure
from backend.services.vision_client import VisionClient
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class FigureAnalyzer:

    def __init__(self):

        self.vision_client = VisionClient()

    def build_prompt(
            self,
            figure: Figure,
            question: str,
            documents: list[Document]
    ) -> tuple[str, str]:
        """
        Builds the prompt sent to the VLM
        """

        system_message = """
You are an expert at interpreting scientific figures from research papers.

You will be provided with:
- The figure image.
- The figure caption.
- Relevant text retrieved from the research paper.
- The user's question.

Instructions:
- Carefully inspect the figure.
- Use the retrieved paper context to better understand the figure and answer the question.
- Use both the visual contents of the figure and the retrieved paper context.
- If the image and the retrieved context disagree, prioritize the information visible in the figure and mention any inconsistency.
- Use the figure caption only as supporting context.
- Do not invent information that is not supported by the figure or the retrieved paper context.
- If the answer cannot be determined from the figure and the retrieved paper context, clearly state that.
""".strip()

        figure_number = figure.figure_number if figure.figure_number is not None else "Unknown"   

        caption = figure.figure_caption if figure.figure_caption else "Not available"

        context = ""
        
        for document in documents:
        
            context += (
                f"Paper: {document.metadata['paper_name']}\n"
                f"Section: {document.metadata['section']}\n\n"
                f"{document.page_content}\n\n"
            )

        user_message = f"""Paper:
{figure.paper_name}

Page:
{figure.page_number}

Figure Number:
{figure_number}

Caption:
{caption}

Relevant Paper Context:
{context}

Question:
{question}
""".strip()

        return system_message, user_message
    

    def analyze(self,
                figure: Figure,
                question: str,
                documents: list[Document]) -> str:

        logger.info(
            f"Analyzing Figure "
            f"{figure.figure_number} "
            f"from paper '{figure.paper_name}'."
        )

        system_message, user_message = self.build_prompt(
            figure=figure,
            question=question,
            documents=documents
        )

        answer = self.vision_client.generate_response(
            system_message=system_message,
            user_message=user_message,
            image_path=figure.image_path,
        )

        logger.info("Figure analysis completed.")

        return answer