from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import QFileDialog

class ReportGenerator:
    def generate_report(self, products):
        report_file = QFileDialog.getSaveFileName(None, "Save Report", "", "PDF Files (*.pdf)")[0]
        if report_file:
            try:
                c = canvas.Canvas(report_file, pagesize=letter)
                c.drawString(100, 750, "Product Report")
                c.drawString(100, 730, "=================")
                y = 700
                for product in products:
                    c.drawString(100, y, f"Name: {product[0]}")
                    c.drawString(250, y, f"Price: {product[1]}")
                    c.drawString(400, y, f"Category: {product[2] if product[2] else 'N/A'}")
                    y -= 20
                    if y < 50:
                        c.showPage()
                        y = 750
                c.save()
                print(f"Report generated successfully: {report_file}")
            except Exception as e:
                print(f"Error generating PDF: {e}")