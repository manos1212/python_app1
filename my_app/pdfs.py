from reportlab.lib.pagesizes import letter, A4
from .models import Appointment
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus.tables import Table, TableStyle, colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER



class NextDayPrint:
   def __init__(self, buffer, pagesize):
       self.buffer = buffer
       if pagesize == 'A4':
           self.pagesize = A4
       elif pagesize == 'Letter':
           self.pagesize = letter
       self.width, self.height = self.pagesize

   def add_page_number(self, canvas, doc):
       canvas.saveState()
       canvas.setFont('Times-Roman', 10)
       page_number_text = "%d" % (doc.page)
       canvas.drawCentredString(
           0.75 * inch,
           0.75 * inch,
           page_number_text
       )
       canvas.restoreState()

   def pdf_tomorrow(self):
       dt_now = datetime.today().date()

       if dt_now.weekday() == 4:
           tomorrow = dt_now + timedelta(days=3)
       elif dt_now.weekday() == 5:
           tomorrow = dt_now + timedelta(days=2)
       else:
           tomorrow = dt_now + timedelta(days=1)
       tomorrows_appoints = Appointment.objects.filter(date_time__contains=tomorrow)

       tomorrows_apps=[]
       total_dose = 0
       app_id =[]
       amka = []
       date = []
       dose = []
       bmi = []
       weight=[]
       for i in tomorrows_appoints:
           d = i.dose
           app_id.append(i.id)
           amka.append(i.amka_id)
           dose.append(i.dose)
           date.append(i.date_time)
           bmi.append(i.bmi)
           weight.append(i.weight)
           total_dose = total_dose + d
           dt = i.date_time.strftime('%H:%M')
           tt=(i.id,i.amka_id,i.weight,i.bmi,i.dose,dt)
           tomorrows_apps.append(tt)

       pfd_title_date=tomorrow.strftime('%Y-%m-%d')

       buffer = self.buffer
       doc = SimpleDocTemplate(buffer,
                               rightMargin=72,
                               leftMargin=72,
                               topMargin=72,
                               bottomMargin=72,
                               pagesize=self.pagesize)

       # Our container for 'Flowable' objects
       elements = []

       # A large collection of style sheets pre-made for us
       styles = getSampleStyleSheet()
       styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

       # Draw things on the PDF. Here's where the PDF generation happens.
       # See the ReportLab documentation for the full list of functionality.

       total_dose = str(round(total_dose, 3))
       tomorrows_apps.insert(0, ['App_Id','       Amka','       Weight','        Bmi', '       Dose', '       Time'])

       table = Table(tomorrows_apps, colWidths=80, rowHeights=40)

       table.setStyle(TableStyle(
           [('LINEABOVE', (0, 0), (-1, 0), 2, colors.aqua),
            ('LINEABOVE', (0, 1), (-1, -1), 0.25, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.aqua),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER')]
       ))
       I = Image('https://ww1.prweb.com/prfiles/2015/12/28/13144702/gI_61269_hm-logo_web.png')
       elements.append(I)
       elements.append(Paragraph(f'Appointments and Total Dose for  {pfd_title_date}', styles['Heading2']))
       elements.append(Spacer(2, 0.3 * inch))
       elements.append(table)
       elements.append(Paragraph('Total Dose:', styles['Heading2']))
       elements.append(Paragraph(total_dose + " MBq", styles['Heading2']))
       doc.build(elements,
                 onFirstPage=self.add_page_number,
                 onLaterPages=self.add_page_number,
                 )

       # Get the value of the BytesIO buffer and write it to the response.
       pdf = buffer.getvalue()
       buffer.close()
       return pdf


class PrevYearPrint:
   def __init__(self, buffer, pagesize):
       self.buffer = buffer
       if pagesize == 'A4':
           self.pagesize = A4
       elif pagesize == 'Letter':
           self.pagesize = letter
       self.width, self.height = self.pagesize

   def add_page_number(self, canvas, doc):
       canvas.saveState()
       canvas.setFont('Times-Roman', 10)
       page_number_text = "%d" % (doc.page)
       canvas.drawCentredString(
           0.75 * inch,
           0.75 * inch,
           page_number_text
       )
       canvas.restoreState()

   def pdf_tomorrow(self):
       dt_now = datetime.today().date()

       prev_year = dt_now - timedelta(days=365)
       last_year = prev_year.year
       prev_year_appoints = Appointment.objects.filter(date_time__contains=last_year)
       total_dose = 0
       total_bmi = 0
       appoint_id = []
       amka = []
       bmi = []
       dose = []
       date1 = []
       weight = []
       prev_year_apps= []

       for i in prev_year_appoints:
           d = i.dose
           bmi_n = i.bmi
           appoint_id.append(i.id)
           amka.append(i.amka)
           weight.append(i.weight)
           bmi.append(i.bmi)
           dose.append(i.dose)
           date1.append(i.date_time)
           total_bmi = total_bmi + bmi_n
           total_dose = total_dose + d
           dt = i.date_time.strftime('%m-%d %H:%M')
           tt=(i.id,i.amka,i.weight,i.bmi,i.dose,dt)
           prev_year_apps.append(tt)

       avg_bmi = total_bmi / len(bmi)
       avg_dose = total_dose / len(dose)

       buffer = self.buffer
       doc = SimpleDocTemplate(buffer,
                               rightMargin=72,
                               leftMargin=72,
                               topMargin=72,
                               bottomMargin=72,
                               pagesize=self.pagesize)

       # Our container for 'Flowable' objects
       elements = []

       # A large collection of style sheets pre-made for us
       styles = getSampleStyleSheet()
       styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

       # Draw things on the PDF. Here's where the PDF generation happens.
       # See the ReportLab documentation for the full list of functionality.

       avg_dose = str(round(avg_dose, 4))
       avg_bmi  = str(round(avg_bmi, 4))
       prev_year_apps.insert(0, ['Appoint_Id','       Amka', '      Weight''                     Bmi',
                                 '                                     Dose',
                                 '                                Date/Time'])

       table = Table(prev_year_apps, colWidths=80, rowHeights=40)

       table.setStyle(TableStyle(
           [('LINEABOVE', (0, 0), (-1, 0), 2, colors.lightskyblue),
            ('LINEABOVE', (0, 1), (-1, -1), 0.25, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.lightskyblue),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER')]
       ))
       I = Image(
           'https://ww1.prweb.com/prfiles/2015/12/28/13144702/gI_61269_hm-logo_web.png')
       elements.append(I)
       elements.append(Spacer(2, 0.3 * inch))
       elements.append(Paragraph('Year: '+str(last_year), styles['Heading2']))
       elements.append(Paragraph('Average Dose: '+avg_dose, styles['Heading2']))
       # elements.append(Paragraph(avg_dose, styles['Heading2']))
       elements.append(Paragraph('Average Bmi: '+avg_bmi, styles['Heading2']))
       # elements.append(Paragraph(avg_bmi, styles['Heading2']))
       elements.append(table)
       doc.build(elements,
                 onFirstPage=self.add_page_number,
                 onLaterPages=self.add_page_number,
                 )

       # Get the value of the BytesIO buffer and write it to the response.
       pdf = buffer.getvalue()
       buffer.close()
       return pdf
