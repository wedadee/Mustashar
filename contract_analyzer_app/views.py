from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
import os
from .services import process_pdf_and_analyze_clauses

def upload_pdf(request):
    """Handle PDF upload and return clause analysis as JSON."""
    # print(f"Request method: {request.method}")
    # print(f"FILES: {request.FILES}")
    # print(f"POST data: {request.POST}")
    
    if request.method == 'POST' and request.FILES.get('contractFile'):
        pdf_file = request.FILES['contractFile']
        contract_type = request.POST.get('contract-type', 'ambiguous_contract')
        # print(f"Received file: {pdf_file.name}")
        # print(f"Contract type: {contract_type}")
        
        # Validate file type
        if not pdf_file.content_type == 'application/pdf':
            return JsonResponse(
                {"error": "الملف غير مدعوم", "details": "يرجى رفع ملف بصيغة PDF"},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )
        
        # Save the uploaded PDF temporarily
        file_path = default_storage.save('temp.pdf', ContentFile(pdf_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        # print(f"Saved PDF to: {full_path}")
        
        try:
            # Process PDF and get clause analysis
            clauses = process_pdf_and_analyze_clauses(full_path, contract_type)
            # print(f"Clauses: {clauses}")
            # Return JSON response
            return JsonResponse(
                {"clauses": clauses},
                json_dumps_params={'ensure_ascii': False}
            )
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return JsonResponse(
                {"error": "فشل في معالجة الملف", "details": str(e)},
                status=500,
                json_dumps_params={'ensure_ascii': False}
            )
        finally:
            # Clean up temporary file
            if os.path.exists(full_path):
                print(f"Cleaning up: {full_path}")
                os.remove(full_path)
    
    # For GET requests or invalid POST, render the form
    return render(request, 'contract_analyzer_app/contract.html')