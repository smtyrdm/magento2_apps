from odoo import models, fields, api, _
import base64, csv, io
from PyPDF2 import PdfReader, PdfWriter

class SaleBatchTransferWiz(models.TransientModel):
    _inherit = 'sale.batch.transfer.wiz'

    pdf_file = fields.Binary("PDF File")
    pdf_filename = fields.Char("PDF Filename")
    
    def _get_picking_pdf(self, picking_ids):
        """
        Multi-company uyumlu toplu PDF oluşturur.
        Her picking kendi company context'inde render edilir ve PDF'ler birleştirilir.
        """
        report = self.env.ref('stock.action_report_delivery')
        pdfs = []

        # Her picking için PDF üret
        for picking in picking_ids:
            company = picking.company_id.id
            main_company = self.env.ref("base.main_company") # tiskönig
            ref_company_ids = picking.partner_id.parent_id.ref_company_ids
            if ref_company_ids and main_company.id not in ref_company_ids.ids:
                company = ref_company_ids[0].id


            ctx = dict(self.env.context, company_id=company, lang=picking.partner_id.lang or 'de_DE')
            pdf_content, _ = report.with_context(ctx)._render_qweb_pdf([picking.id])
            pdfs.append(pdf_content)

        # PDF'leri birleştir
        writer = PdfWriter()
        for pdf_bytes in pdfs:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        # Base64 encode
        self.pdf_file = base64.b64encode(output.read())
        self.pdf_filename = f"{fields.Date.today()}_lieferungen.pdf"

        # Attachment oluştur
        attachment = self.env['ir.attachment'].create({
            'name': self.pdf_filename,
            'type': 'binary',
            'datas': self.pdf_file,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        return attachment
    

    # def _get_picking_pdf(self, picking_ids):
    #     report = self.env.ref('stock.action_report_delivery')
    #     pdf_content, _ = report._render_qweb_pdf(picking_ids.ids)
    #     self.pdf_file = base64.b64encode(pdf_content)
    #     self.pdf_filename =  str(fields.Date.today()) + "_lieferungen.pdf"
    # 
    #     attachment = self.env['ir.attachment'].create({
    #         'name': self.pdf_filename,
    #         'type': 'binary',
    #         'datas': self.pdf_file.decode('utf-8'),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/pdf',
    #     })
    #     return attachment

        #return {'pdf_file': self.pdf_file, 'pdf_filename': self.pdf_filename}


    