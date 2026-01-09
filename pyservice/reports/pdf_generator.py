"""
PDF Report Generator
PyService Mini-ITSM Platform

Generate PDF reports using ReportLab.
"""

from io import BytesIO
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Base class for PDF report generation."""
    
    def __init__(self, title="Report", author="PyService ITSM"):
        self.title = title
        self.author = author
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a365d')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2c5282')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=28,
            alignment=1,  # Center
            textColor=colors.HexColor('#2d3748')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.HexColor('#718096')
        ))
    
    def create_header(self, elements):
        """Create report header."""
        elements.append(Paragraph(self.title, self.styles['ReportTitle']))
        elements.append(Paragraph(
            f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')} | {self.author}",
            self.styles['Normal']
        ))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e2e8f0')))
        elements.append(Spacer(1, 20))
    
    def create_table(self, data, col_widths=None, header_color='#2c5282'):
        """Create a styled table."""
        table = Table(data, colWidths=col_widths)
        
        style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ])
        
        table.setStyle(style)
        return table
    
    def generate_pdf(self, elements):
        """Generate PDF from elements."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        doc.build(elements)
        buffer.seek(0)
        return buffer


class IncidentReportGenerator(PDFReportGenerator):
    """Generate incident reports."""
    
    def __init__(self, start_date=None, end_date=None):
        super().__init__(title="Incident Report")
        self.start_date = start_date or (timezone.now() - timedelta(days=30)).date()
        self.end_date = end_date or timezone.now().date()
    
    def generate(self):
        """Generate the incident report PDF."""
        from incidents.models import Incident
        from django.db.models import Count
        
        elements = []
        self.create_header(elements)
        
        # Date range
        elements.append(Paragraph(
            f"Period: {self.start_date} to {self.end_date}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 20))
        
        # Get incidents
        incidents = Incident.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        )
        
        # Summary section
        elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        
        total = incidents.count()
        resolved = incidents.filter(state__in=['resolved', 'closed']).count()
        sla_breached = incidents.filter(sla_breached=True).count()
        sla_compliance = ((total - sla_breached) / max(total, 1)) * 100
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Incidents', str(total)],
            ['Resolved', str(resolved)],
            ['SLA Breached', str(sla_breached)],
            ['SLA Compliance', f'{sla_compliance:.1f}%'],
        ]
        
        elements.append(self.create_table(summary_data, col_widths=[3*inch, 2*inch]))
        elements.append(Spacer(1, 20))
        
        # Priority breakdown
        elements.append(Paragraph("By Priority", self.styles['SectionTitle']))
        
        priority_data = [['Priority', 'Count', 'Percentage']]
        for p in incidents.values('priority').annotate(count=Count('id')).order_by('priority'):
            priority_labels = {1: 'P1 - Critical', 2: 'P2 - High', 3: 'P3 - Medium', 4: 'P4 - Low'}
            pct = (p['count'] / max(total, 1)) * 100
            priority_data.append([
                priority_labels.get(p['priority'], f"P{p['priority']}"),
                str(p['count']),
                f'{pct:.1f}%'
            ])
        
        elements.append(self.create_table(priority_data, col_widths=[2.5*inch, 1.5*inch, 1.5*inch]))
        elements.append(Spacer(1, 20))
        
        # Recent incidents table
        elements.append(Paragraph("Recent Incidents", self.styles['SectionTitle']))
        
        incident_data = [['Number', 'Title', 'Priority', 'Status', 'Created']]
        for inc in incidents.order_by('-created_at')[:20]:
            incident_data.append([
                inc.number,
                inc.title[:30] + ('...' if len(inc.title) > 30 else ''),
                f'P{inc.priority}',
                inc.get_state_display(),
                inc.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        elements.append(self.create_table(
            incident_data,
            col_widths=[1.2*inch, 2*inch, 0.8*inch, 1*inch, 1.5*inch]
        ))
        
        return self.generate_pdf(elements)


class AssetInventoryReportGenerator(PDFReportGenerator):
    """Generate asset inventory reports."""
    
    def __init__(self):
        super().__init__(title="Asset Inventory Report")
    
    def generate(self):
        """Generate the asset inventory report PDF."""
        from cmdb.models import Asset
        from django.db.models import Count
        
        elements = []
        self.create_header(elements)
        
        assets = Asset.objects.all()
        
        # Summary
        elements.append(Paragraph("Inventory Summary", self.styles['SectionTitle']))
        
        summary_data = [
            ['Status', 'Count'],
            ['Total Assets', str(assets.count())],
            ['In Stock', str(assets.filter(status='in_stock').count())],
            ['Assigned', str(assets.filter(status='assigned').count())],
            ['In Repair', str(assets.filter(status='in_repair').count())],
            ['Retired', str(assets.filter(status='retired').count())],
        ]
        
        elements.append(self.create_table(summary_data, col_widths=[3*inch, 2*inch]))
        elements.append(Spacer(1, 20))
        
        # By type
        elements.append(Paragraph("By Asset Type", self.styles['SectionTitle']))
        
        type_data = [['Type', 'Count', 'Assigned', 'Available']]
        for at in assets.values('asset_type').annotate(count=Count('id')).order_by('-count'):
            assigned = assets.filter(asset_type=at['asset_type'], status='assigned').count()
            available = assets.filter(asset_type=at['asset_type'], status='in_stock').count()
            type_data.append([
                at['asset_type'].replace('_', ' ').title(),
                str(at['count']),
                str(assigned),
                str(available)
            ])
        
        elements.append(self.create_table(type_data))
        elements.append(Spacer(1, 20))
        
        # Asset list
        elements.append(Paragraph("Asset Details", self.styles['SectionTitle']))
        
        asset_data = [['Name', 'Type', 'Serial Number', 'Status', 'Assigned To']]
        for asset in assets.select_related('assigned_to').order_by('-created_at')[:50]:
            asset_data.append([
                asset.name[:25] + ('...' if len(asset.name) > 25 else ''),
                asset.get_asset_type_display(),
                asset.serial_number or '-',
                asset.get_status_display(),
                asset.assigned_to.username if asset.assigned_to else '-'
            ])
        
        elements.append(self.create_table(
            asset_data,
            col_widths=[1.5*inch, 1.2*inch, 1.3*inch, 1*inch, 1.2*inch]
        ))
        
        return self.generate_pdf(elements)


class SLAComplianceReportGenerator(PDFReportGenerator):
    """Generate SLA compliance reports."""
    
    def __init__(self, start_date=None, end_date=None):
        super().__init__(title="SLA Compliance Report")
        self.start_date = start_date or (timezone.now() - timedelta(days=30)).date()
        self.end_date = end_date or timezone.now().date()
    
    def generate(self):
        """Generate the SLA compliance report PDF."""
        from incidents.models import Incident
        from cmdb.models import User
        from django.db.models import Count, Avg, F
        
        elements = []
        self.create_header(elements)
        
        elements.append(Paragraph(
            f"Period: {self.start_date} to {self.end_date}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 20))
        
        incidents = Incident.objects.filter(
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        )
        
        # Overall SLA metrics
        elements.append(Paragraph("Overall SLA Metrics", self.styles['SectionTitle']))
        
        total = incidents.count()
        breached = incidents.filter(sla_breached=True).count()
        compliance = ((total - breached) / max(total, 1)) * 100
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Incidents', str(total)],
            ['SLA Breached', str(breached)],
            ['SLA Compliance Rate', f'{compliance:.1f}%'],
        ]
        
        elements.append(self.create_table(metrics_data, col_widths=[3*inch, 2*inch]))
        elements.append(Spacer(1, 20))
        
        # By priority
        elements.append(Paragraph("SLA by Priority", self.styles['SectionTitle']))
        
        priority_data = [['Priority', 'Total', 'Breached', 'Compliance']]
        for p in [1, 2, 3, 4]:
            p_total = incidents.filter(priority=p).count()
            p_breached = incidents.filter(priority=p, sla_breached=True).count()
            p_compliance = ((p_total - p_breached) / max(p_total, 1)) * 100
            priority_labels = {1: 'P1 - Critical', 2: 'P2 - High', 3: 'P3 - Medium', 4: 'P4 - Low'}
            priority_data.append([
                priority_labels[p],
                str(p_total),
                str(p_breached),
                f'{p_compliance:.1f}%'
            ])
        
        elements.append(self.create_table(priority_data))
        elements.append(Spacer(1, 20))
        
        # SLA breached incidents
        breached_incidents = incidents.filter(sla_breached=True).order_by('-created_at')[:20]
        
        if breached_incidents.exists():
            elements.append(Paragraph("SLA Breached Incidents", self.styles['SectionTitle']))
            
            breach_data = [['Number', 'Title', 'Priority', 'Due Date', 'Assigned To']]
            for inc in breached_incidents:
                breach_data.append([
                    inc.number,
                    inc.title[:25] + ('...' if len(inc.title) > 25 else ''),
                    f'P{inc.priority}',
                    inc.due_date.strftime('%Y-%m-%d %H:%M') if inc.due_date else '-',
                    inc.assigned_to.username if inc.assigned_to else '-'
                ])
            
            elements.append(self.create_table(breach_data))
        
        return self.generate_pdf(elements)


def generate_incident_report_response(start_date=None, end_date=None):
    """Generate incident report and return HTTP response."""
    generator = IncidentReportGenerator(start_date, end_date)
    pdf = generator.generate()
    
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="incident_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


def generate_asset_report_response():
    """Generate asset report and return HTTP response."""
    generator = AssetInventoryReportGenerator()
    pdf = generator.generate()
    
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="asset_inventory_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


def generate_sla_report_response(start_date=None, end_date=None):
    """Generate SLA report and return HTTP response."""
    generator = SLAComplianceReportGenerator(start_date, end_date)
    pdf = generator.generate()
    
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sla_compliance_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response
