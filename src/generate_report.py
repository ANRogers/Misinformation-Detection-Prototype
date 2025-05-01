from fpdf import FPDF
import os
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Medical Misinformation Detector Report - All Articles', ln=True, align='C')
        self.ln(8)

    def title_settings(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, title, ln=True)
        self.ln(2)

    def body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()

def export_report_to_pdf(reports):
    output_folder="reports"

    # create report filename useing current time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"article_report_{timestamp}.pdf"
    output_path = os.path.join(output_folder, output_filename)
    
    article_report = PDFReport()
    article_report.add_page()

    report_number = 0
    # Process each report and append it to the same PDF
    for report in reports:
        name, source, source_status, result, warnings = report
        report_number += 1
        # Article Information
        article_report.title_settings(f"Article {report_number} - {name}")
        article_report.body(f"Name/URL: {name}")

        # Source Information
        article_report.title_settings("Source Information")
        article_report.body(f"Source: {source}\nSource Status: {source_status}")

        # Prediction Results
        article_report.title_settings("Prediction Results")
        content_prediction = "Reliable" if result['content_prediction'] == 1 else "Misleading"
        article_report.body(
            f"Content Analysis: {content_prediction}\n"
            f"Confidence: {result['confidence']}\n"
            f"Final Decision: {result['final_decision']}"
        )

        # Warnings
        article_report.title_settings("Warnings and Advice")
        for warning in warnings:
            article_report.body(warning)

        article_report.add_page()  # Add a page break between articles

    # Save the combined report
    article_report.output(output_path)
    print(f" Combined report successfully saved to {os.path.abspath(output_path)}")

