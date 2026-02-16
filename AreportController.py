# AreportController.py - FINAL VERSION (Clean PDF, No HTML Tags)
from AreportModel import ReportsModel
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from datetime import datetime

# PDF Imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


class ReportsController:
    def __init__(self, user_data=None):
        self.model = ReportsModel()
        self.view = None
        self.user_data = user_data
        self.current_report_data = []
        self.current_report_type = ""
        self.current_date_range = {"start": "", "end": ""}

    def set_view(self, view):
        self.view = view
        self.view.generate_btn.clicked.connect(self.handle_generate_report)
        self.view.export_btn.clicked.connect(self.handle_export_report)
        self.load_report_history()

    def load_report_history(self):
        """Loads the list of previously generated reports"""
        try:
            reports = self.model.get_all_saved_reports()
            if self.view:
                self.view.load_reports(reports)
        except Exception as e:
            print(f"Error loading history: {e}")

    def handle_generate_report(self):
        """Fetch specific data based on dropdown selection and display it"""
        rtype = self.view.report_type_combo.currentText()
        start = self.view.start_date.date().toString("yyyy-MM-dd")
        end = self.view.end_date.date().toString("yyyy-MM-dd")

        self.current_report_type = rtype
        self.current_date_range = {"start": start, "end": end}
        data = []

        try:
            if rtype == "Stock Movement":
                data = self.model.get_stock_movement(start, end)
            elif rtype == "Inventory Status":
                data = self.model.get_inventory_status()
            elif rtype == "Defects Report":
                data = self.model.get_defective_report(start, end)
            elif rtype == "User Activity":
                data = self.model.get_user_activity(start, end)

            self.current_report_data = data

            if data:
                self.view.display_generated_data(data)
                print(f"✓ Generated {len(data)} rows for {rtype}")
            else:
                self.view.display_generated_data([])
                self.show_styled_message("No Data",
                                         f"No data found for {rtype} in the selected date range.",
                                         "Warning")

            if data:
                self.model.save_report_entry(rtype, start, end, self.user_data, transaction_id=None)

        except Exception as e:
            print(f"Report Generation Error: {e}")
            import traceback
            traceback.print_exc()
            self.show_styled_message("Error", f"Failed to generate report: {e}", "Critical")

    def handle_export_report(self):
        """Export the currently displayed report to PDF"""
        if not self.current_report_data:
            self.show_styled_message("Error", "No data to export. Please generate a report first.", "Warning")
            return

        default_filename = f"{self.current_report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self.view,
            "Save PDF Report",
            default_filename,
            "PDF Files (*.pdf)"
        )

        if filename:
            try:
                self.generate_pdf(filename)
                self.show_styled_message("Success",
                                         f"Report exported successfully to:\n{filename}",
                                         "Info")
            except Exception as e:
                print(f"PDF Export Error: {e}")
                import traceback
                traceback.print_exc()
                self.show_styled_message("Error", f"Export failed: {e}", "Critical")

    def generate_pdf(self, filename):
        """Generate professional PDF report - NO HTML TAGS"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=1 * inch,
            bottomMargin=0.75 * inch
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#0076aa"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor("#333333"),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        # ============================================
        # 1. REPORT HEADER
        # ============================================
        title = Paragraph("PyesaTrak Inventory Management System", title_style)
        elements.append(title)

        subtitle = Paragraph(f"{self.current_report_type}", header_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 20))

        # ============================================
        # 2. REPORT METADATA (Clean Table - No HTML)
        # ============================================

        # Get user info
        if self.user_data:
            fname = self.user_data.get('userFname', '')
            lname = self.user_data.get('userLname', '')
            full_name = f"{fname} {lname}".strip() if fname or lname else self.user_data.get('username', 'Unknown')
        else:
            full_name = "System Admin"

        # Current timestamp
        transaction_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        # Create metadata table WITHOUT HTML tags
        metadata = [
            ["Requested By:", full_name],
            ["Processed By:", full_name],
            ["Transaction Date:", transaction_datetime],
            ["Validated By:", "_____________________"],
        ]

        # Add date range if applicable
        if self.current_report_type != "Inventory Status":
            metadata.append([
                "Report Period:",
                f"{self.current_date_range['start']} to {self.current_date_range['end']}"
            ])

        metadata.append(["Total Records:", str(len(self.current_report_data))])

        # Style the table - First column bold via TableStyle
        meta_table = Table(metadata, colWidths=[2 * inch, 4 * inch])
        meta_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),  # Label column - BOLD
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),  # Value column - NORMAL
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333333")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))

        elements.append(meta_table)
        elements.append(Spacer(1, 30))

        # ============================================
        # 3. REPORT DATA TABLE
        # ============================================

        if not self.current_report_data:
            no_data = Paragraph("No data available for this selection.", styles['Normal'])
            elements.append(no_data)
        else:
            # Extract headers and data
            headers = [k.replace('_', ' ').title() for k in self.current_report_data[0].keys()]
            data_rows = [headers]

            # Add data rows
            for row in self.current_report_data:
                row_data = []
                for val in row.values():
                    if val is None:
                        row_data.append("")
                    else:
                        row_data.append(str(val))
                data_rows.append(row_data)

            # Create table
            data_table = Table(data_rows)
            data_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0076aa")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),

                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]))

            elements.append(data_table)

        # ============================================
        # 4. VALIDATION SIGNATURE SECTION
        # ============================================
        elements.append(Spacer(1, 40))

        validation_section = Paragraph("Validation & Approval", header_style)
        elements.append(validation_section)
        elements.append(Spacer(1, 10))

        # Clean signature table - NO HTML
        signature_data = [
            ["Validated By:", "_____________________", "Date:", "_____________________"],
            ["", "", "", ""],
            ["Signature:", "_____________________", "Position:", "_____________________"],
        ]

        sig_table = Table(signature_data, colWidths=[1.2 * inch, 2 * inch, 0.8 * inch, 2 * inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('FONT', (3, 0), (3, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333333")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(sig_table)

        # ============================================
        # 5. FOOTER NOTE
        # ============================================
        elements.append(Spacer(1, 30))

        footer_note = Paragraph(
            "<i>This is a computer-generated report from PyesaTrak Inventory Management System. "
            "All data is accurate as of the transaction date listed above.</i>",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        elements.append(footer_note)

        # Build PDF
        doc.build(elements)
        print(f"✓ PDF exported: {filename}")

    def show_styled_message(self, title, text, icon_type):
        """Show styled message dialog"""
        msg = QMessageBox(self.view)
        msg.setWindowTitle(title)
        msg.setText(text)

        if icon_type == "Info":
            msg.setIcon(QMessageBox.Icon.Information)
        elif icon_type == "Warning":
            msg.setIcon(QMessageBox.Icon.Warning)
        elif icon_type == "Critical":
            msg.setIcon(QMessageBox.Icon.Critical)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #0076aa;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #005580;
            }
        """)

        msg.exec()