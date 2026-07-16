"""
Generate a test PDF report and upload it to the InsightAgent backend.
This ensures we have local documents for local_only and hybrid routing tests.
"""
import os
import sys
import requests
import fitz  # PyMuPDF

# Reconfigure stdout to use UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def generate_pdf(filename: str):
    """Generate a 3-page mock PDF with PyMuPDF."""
    doc = fitz.open()

    # Page 1: Title and Overview
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Pakistan IT Export Growth and Policy Report 2024", fontsize=16, color=(0, 0, 0))
    page1.insert_text((50, 80), "Published: June 2024 by Pakistan Software Houses Association (P@SHA)", fontsize=10, color=(0.3, 0.3, 0.3))

    p1_body = (
        "Executive Summary:\n"
        "This report outlines the performance of Pakistan's Information Technology (IT) and IT-enabled Services (ITeS) sectors.\n"
        "In the fiscal year 2023-2024, Pakistan's IT exports reached a record high of $2.5 billion, representing a significant growth\n"
        "rate of 12% compared to the previous fiscal year's value of $2.2 billion. The growth is primarily driven by mobile app\n"
        "development, enterprise software development, and freelance services."
    )
    page1.insert_text((50, 120), p1_body, fontsize=11, color=(0, 0, 0))

    # Page 2: Tax Policies and Government Initiatives
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Government Policies and Incentives (2024 Status)", fontsize=14, color=(0, 0, 0))

    p2_body = (
        "Key Policies:\n"
        "1. Income Tax Exemption: The government offers a 100% tax credit on export proceeds from IT services up to June 30, 2025,\n"
        "   subject to a nominal final tax rate of 0.25% of export value, provided that at least 80% of export proceeds are brought\n"
        "   into the country through normal banking channels.\n"
        "2. Foreign Currency Retention: Exporters can retain up to 35% of their export proceeds in special foreign currency accounts\n"
        "   (ESFCAs) to pay for international software licenses, SaaS subscriptions, and digital marketing costs.\n"
        "3. Special Technology Zones Authority (STZA): STZA provides 10-year tax exemptions for zone enterprises and developers."
    )
    page2.insert_text((50, 100), p2_body, fontsize=11, color=(0, 0, 0))

    # Page 3: Key Challenges and Projections
    page3 = doc.new_page()
    page3.insert_text((50, 50), "Challenges & Future Projections", fontsize=14, color=(0, 0, 0))

    p3_body = (
        "Challenges:\n"
        "The sector faces infrastructure bottlenecks, including unstable internet connectivity in smaller cities and limited access\n"
        "to international payment gateways like PayPal. High cost of doing business and brain drain are major concerns.\n\n"
        "Projections:\n"
        "Analysts predict that if the current 0.25% tax policy remains stable, exports could reach $3.5 billion by 2026.\n"
        "However, any increase in tax rates could decelerate this growth to under 5% per annum."
    )
    page3.insert_text((50, 100), p3_body, fontsize=11, color=(0, 0, 0))

    doc.save(filename)
    doc.close()
    print(f"Generated test PDF file: {filename}")


def upload_pdf(filename: str, upload_url: str):
    """Upload the generated PDF to the FastAPI endpoint."""
    if not os.path.exists(filename):
        print(f"Error: {filename} does not exist.")
        return False

    print(f"Uploading {filename} to {upload_url}...")
    try:
        with open(filename, 'rb') as f:
            files = {'file': (os.path.basename(filename), f, 'application/pdf')}
            response = requests.post(upload_url, files=files)
            if response.status_code == 200:
                print("Upload response:", response.json())
                print("✅ Successfully uploaded and indexed document.")
                return True
            else:
                print(f"❌ Failed to upload. Status code: {response.status_code}, Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error during upload: {str(e)}")
        return False


def main():
    pdf_filename = "pakistan_it_report_2024.pdf"
    url = "http://localhost:8000/api/upload"
    generate_pdf(pdf_filename)
    success = upload_pdf(pdf_filename, url)
    
    # Clean up the local pdf file since it's now in the backend's upload store
    if success and os.path.exists(pdf_filename):
        os.remove(pdf_filename)
        print(f"Cleaned up local file: {pdf_filename}")


if __name__ == "__main__":
    main()
