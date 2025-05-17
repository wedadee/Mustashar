import google.generativeai as genai
from django.conf import settings
import json
import re
from datetime import datetime

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_with_gemini(pdf_path):
    """Extract text from a PDF using Gemini."""
    print(f"Extracting text from: {pdf_path}")
    pdf_file = genai.upload_file(path=pdf_path, mime_type="application/pdf")
    prompt = (
        "Extract all text from this PDF, including Arabic, English, numbers, and symbols like %. "
        "Ensure dates are extracted accurately in the format DD-MM-YYYY. "
        "Return the text as-is, preserving the original content."
    )
    response = model.generate_content([pdf_file, prompt])
    extracted_text = response.text.strip()
    genai.delete_file(pdf_file.name)
    return extracted_text

def process_pdf_with_gemini(pdf_path):
    """Process PDF and extract text using Gemini."""
    extracted_text = extract_text_with_gemini(pdf_path)
    result = f"Extracted Text:\n{extracted_text}\n"
    return result

def extract_contract_clauses(contract_text):
    """Extract contract clauses using Gemini."""
    prompt = f"""
        قم باستخراج جميع بنود العقد من النص التالي. تأكد من اتباع التعليمات التالية بدقة:

        1. استخرج فقط النصوص التي تمثل بنودًا في العقد.
        2. تجاهل أي نص غير متعلق بالبنود، مثل العناوين، الترويسات، الأرقام، التواقيع، أو أي نص غير ذي صلة.
        3. لكل بند، قم بتقديمه بالتنسيق التالي:
           بند رقم X: [نص البند كما هو في العقد]
        4. حافظ على التسلسل الأصلي للبنود كما وردت في النص.
        5. إذا كان النص يحتوي على فقرات غير واضحة كبنود، قم بتجاهلها إلا إذا كانت تحتوي على مصطلحات مثل "يلتزم"، "يتعهد"، "يحق"، أو أي مصطلحات قانونية تشير إلى أنها بند.
        6. تحقق من صحة التواريخ في البنود (مثل أن تكون تواريخ النهاية بعد تواريخ البداية) 
        النص:
        {contract_text}

        المخرجات المتوقعة:
        - قائمة بجميع بنود العقد، مرقمة ومصاغة كما هي في النص الأصلي.
        - لا تقم بإضافة أي تفسيرات أو تعديلات على النص.
    """
    response = model.generate_content(prompt)
    clauses = response.text.strip()
    return clauses

def correct_dates_in_text(text):
    date_pattern = re.compile(r"\d{2}-\d{2}-\d{4}")
    dates = date_pattern.findall(text)
    corrected_text = text
    for date_str in dates:
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            print(f"Suspicious or invalid date format found: {date_str}")
            # Optionally log or highlight for manual review
    return corrected_text

def analyze_contract_with_gemini(clauses):
    """Analyze contract for ambiguous clauses and return structured JSON data directly."""
    prompt = f"""
        قم بتحليل العقد التالي وتحديد البنود الغامضة فيه.
        
        النص:
        {clauses}

        المطلوب:
        - قم بإرجاع نتائج التحليل بصيغة JSON فقط، دون أي نصوص إضافية.
        - لكل بند غامض، أدرج:
          - "clause": نص البند كما هو.
          - "problem": سبب الغموض.
          - "recommendation": اقتراح لإعادة صياغته.
        - تحقق من التواريخ للتأكد من أنها منطقية (مثل أن تكون تواريخ النهاية بعد تواريخ البداية).

        مثال على التنسيق:
        [
            {{
                "clause": "الطرف الأول يلتزم بتوفير الخدمة حسب الظروف المتاحة.",
                "problem": "غير واضح ما المقصود بـ'الظروف المتاحة'.",
                "recommendation": "يُحدد نطاق الخدمات ومدى توافرها بدقة."
            }}
        ]

        إذا لم توجد بنود غامضة، أعد JSON فارغة مثل: []
    """
    try:
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        analysis_json = response.text.strip()
        parsed_clauses = json.loads(analysis_json)
        return parsed_clauses
    except Exception as e:
        print(f"Gemini API error or invalid JSON: {e}")
        return []

def analyze_contradictory_clauses_with_gemini(clauses):
    """Analyze contract for contradictory clauses and return structured JSON data directly."""
    print(f"Analyzing contradictory clauses: {clauses}")
    prompt = f"""
        قم بتحليل العقد التالي وتحديد البنود المتناقضة فيه.

        النص:
        {clauses}

        المطلوب:
        - قم بإرجاع نتائج التحليل بصيغة JSON فقط، دون أي نصوص إضافية.
        - لكل مجموعة من البنود المتناقضة، أدرج:
          - "clause1": نص البند الأول كما هو.
          - "clause2": نص البند الثاني كما هو (أو فارغ إذا كان التناقض مع نص خارجي).
          - "contradiction": شرح التناقض بين البندين (أو بين البند ونص خارجي).
          - "recommendation": اقتراح لتسوية التناقض.
        - ركز على التناقضات مثل الالتزامات المتناقضة، الحقوق المتباينة، أو الشروط المعارضة.
        - تحقق من التواريخ للتأكد من أنها منطقية (مثل أن تكون تواريخ النهاية بعد تواريخ البداية). إذا تم العثور على تاريخ غير منطقي، قم بتضمينه كجزء من التناقض.

        مثال على التنسيق:
        [
            {{
                "clause1": "الطرف الأول يلتزم بتسليم العمل خلال 30 يومًا.",
                "clause2": "الطرف الأول يلتزم بتسليم العمل خلال 60 يومًا.",
                "contradiction": "البندان يحددان فترتين مختلفتين لتسليم العمل.",
                "recommendation": "توحيد المدة إلى فترة واحدة، مثل: 'الطرف الأول يلتزم بتسليم العمل خلال 45 يومًا.'"
            }}
        ]

        إذا لم توجد بنود متناقضة، أعد JSON فارغة مثل: []
    """
    try:
        generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        analysis_json = response.text.strip()
        parsed_clauses = json.loads(analysis_json)
        return parsed_clauses
    except Exception as e:
        print(f"Gemini API error or invalid JSON for contradictory analysis: {e}")
        return []

def process_pdf_and_analyze_clauses(pdf_path, contract_type='ambiguous_contract'):
    """Process PDF and return clause analysis based on contract type."""
    extracted_text = process_pdf_with_gemini(pdf_path)
    extracted_text=correct_dates_in_text(extracted_text)
    clauses = extract_contract_clauses(extracted_text)
    if contract_type == 'ambiguous_contract':
        return analyze_contract_with_gemini(clauses)
    elif contract_type == 'Contradictory_contract':
        return analyze_contradictory_clauses_with_gemini(clauses)
    else:
        print(f"Invalid contract type: {contract_type}")
        return []