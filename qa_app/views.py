
from django.shortcuts import render
from django.http import JsonResponse
from .services import QAService
import logging

logger = logging.getLogger(__name__)
qa_service = QAService.get_instance()

def qa_api(request):
    """API endpoint for QA."""
    if request.method == "POST":
        query = request.POST.get("query", "")
        if not query:
            return JsonResponse({"error": "Query is required"}, status=400)

        try:
            logger.info(f"Processing query: {query}")
            result = qa_service.answer_question(query)
            return JsonResponse({
                "query": query,
                "answer": result["answer"],
                "sources": result["sources"]
            })
        except Exception as e:
            logger.error(f"Error processing API query: {e}", exc_info=True)
            return JsonResponse({"error": "An error occurred"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def qa_view(request):
    """Render the QA interface."""
    if request.method == "POST":
        query = request.POST.get("query", "")
        if not query:
            return render(request, "qa_app/question.html", {"error": "يرجى إدخال سؤال"})

        try:
            result = qa_service.answer_question(query)
            return render(request, "qa_app/question.html", {
                "query": query,
                "answer": result["answer"],
                "sources": result["sources"]
            })
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return render(request, "qa_app/question.html", {"error": "حدث خطأ أثناء معالجة السؤال"})

    return render(request, "qa_app/question.html")