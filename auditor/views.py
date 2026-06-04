# Django core imports
from django.shortcuts import render, redirect
from django.views import View

# Local imports — models and AI utility functions
from .models import *
from .ai_utility import *


class DashboardView(View):
    """Shows all uploaded contracts in a table."""

    def get(self, request):
        # Fetch all contracts, newest first
        all_contracts = Contract.objects.all().order_by('-id')
        return render(request, 'dashboard.html', {'contracts': all_contracts})  


class ContractUploadView(View):
    """Handles PDF upload, AI analysis, and saving result to DB."""

    def get(self, request):
        # Simply render the upload form
        return render(request, 'upload.html')

    def post(self, request):
        # Step 1 — Get uploaded file and vendor name from form
        pdf_file = request.FILES.get('contract_pdf')
        vendor = request.POST.get('vendor_name', 'Unknown Vendor')

        # Step 2 — Validate: file must exist
        if not pdf_file:
            return render(request, 'upload.html', {"error": "No file uploaded"}, status=400)

        # Step 3 — Validate: file must be a PDF
        if not pdf_file.name.lower().endswith(".pdf"):
            return render(request, 'upload.html', {"error": "Only PDFs are allowed"}, status=400)

        try:
            # Step 4 — Extract raw text from PDF
            extract = extract_text_from_pdf(pdf_file)

            # Step 5 — Send text to Gemini and get AI analysis
            analyze = analyze_contract_with_ai(extract)

            # Step 6 — Default risk score fallback
            risk_score = 50

            # Step 7 — Parse actual risk score from Gemini response
            for line in analyze.splitlines():
                if "RISK_SCORE:" in line:
                    try:
                        risk_score = int(line.split(":")[1].strip().replace("*", ""))
                    except:
                        risk_score = 50

            # Step 8 — Save vendor, AI summary and risk score to DB
            Contract.objects.create(
                vendor_name=vendor,
                ai_summary=analyze,
                risk_score=risk_score
            )

            # Step 9 — Redirect to dashboard on success
            return redirect('contract-dashboard')

        except Exception as e:
            # If anything fails — show clean error, don't crash
            error_msg = "Google AI Server is currently busy. Please click 'Analyze' again in 10 seconds!"
            return render(request, 'upload.html', {'error': error_msg})