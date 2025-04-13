from enum import Enum
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class CaseStatus(str, Enum):
    '''
        Enum defined for case status
    '''
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"


class PdfGenerator:
    '''
        Pdf generator function
    '''
    def __init__(self):
        self.buffer = io.BytesIO()
        self.doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.elements = []

    
    def generate_pdf(self, case_data, case_hearing_data, case_order_data, case_advocate_data):
        '''
            function to generate function
        '''
        # Title
        self.elements.append(Paragraph("CASE SUMMARY", self.styles['Title']))
        self.elements.append(Spacer(1, 12))


        # case info table
        case_info = self.case_data_generation(case_data)
        self.elements.append(Paragraph("Case Details", self.styles['Heading2']))
        self.elements.append(Table(case_info, hAlign='LEFT'))
        self.elements.append(Spacer(1, 12))


        # case hearing table
        self.elements.append(Paragraph("Case Hearings", self.styles['Heading2']))
        self.case_hearing_data_generator(case_hearing_data)
        self.elements.append(Spacer(1, 12))

        
        # case orders table
        self.elements.append(Paragraph("Case Orders", self.styles['Heading2']))
        self.case_order_data_generator(case_order_data)
        self.elements.append(Spacer(1, 12))

        
        # advocates case table
        self.elements.append(Paragraph("Case Advocates", self.styles['Heading2']))
        self.advocate_case_data_generator(case_advocate_data)

        # Building pdf
        self.doc.build(self.elements)
        self.buffer.seek(0)


    def case_data_generation(self, data):
        '''
            case data generation helper function
        '''
        case_info = [
            ["Case Number", data["case_number"]],
            ["Case Title", data["case_title"]],
            ["Court Name", data["court_name"]],
            ["Filing Date", data["filing_date"]],
            ["Upcoming Hearing Date", data["upcoming_hearing_date"]],
            ["Case Status", data["case_status"].value.upper()],
        ]

        return case_info
    

    def case_hearing_data_generator(self, data):
        '''
            helper function related to case hearing data
        '''
        if data:
            hearing_data = [["Date", "Judge", "Rival Advocate", "Notes"]]
            for h in data:
                hearing_data.append([
                h.get("hearing_date", "N/A"),
                Paragraph(h.get("Judge", "N/A"), self.styles['Normal']),
                Paragraph(h.get("rival_advocate_name", "N/A") or "N/A", self.styles['Normal']),
                Paragraph(h.get("hearing_notes", "N/A") or "N/A", self.styles['Normal'])
                ])
            table = Table(hearing_data, hAlign='LEFT', colWidths=[60, 100, 100, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            self.elements.append(table)


        else:
            self.elements.append(Paragraph("No hearing records.", self.styles['Normal']))

     
    def case_order_data_generator(self, data):
        '''
            Case order data in pdf helper function
        '''
        if data:
            order_data = [["Order date", "Order details"]]
            for o in data:
                order_data.append([
                o.get("order_date"),
                Paragraph(o.get("order_details", "N/A"), self.styles['Normal'])
            ])
        
            table = Table(order_data, hAlign='LEFT', colWidths=[60, 400])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            self.elements.append(table)

        else:
            self.elements.append(Paragraph("No orders available.", self.styles['Normal']))


    def advocate_case_data_generator(self, data):
        if data:
            advocate_data = [["Name", "Phone", "Email", "Bar Council Number"]]
            for adv in data:
                advocate_data.append([
                    adv.get("name"),
                    adv.get("phone_number"),
                    adv.get("email"),
                    adv.get("bar_council_number")
                ])
            table = Table(advocate_data, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            self.elements.append(table)

        else:
            self.elements.append(Paragraph("No advocates assigned.", self.styles['Normal']))
