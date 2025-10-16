from odoo import models, fields, api, _
import base64, logging, csv
import io, zipfile
import re
import logging
_logger = logging.getLogger(__name__)
class SaleBatchTransferWiz(models.TransientModel):
    _name = 'sale.batch.transfer.wiz'
    _description = 'Sale Batch Transfer Wiz'

    printer_id = fields.Selection([
        ('printer1', 'Tisch Office Printer'),
        ('printer2', 'Tisch Manufacture Printer')
    ], string='Printer')

    def action_confirm(self):
        order_line = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        data = {}
        picking_ids = self._get_picking_confirm(order_line)
        if not picking_ids:
            raise models.ValidationError(_('No picking confirmed.'))
            
        data['picking_ids'] = picking_ids
        data['pdf'] = self._get_picking_pdf(picking_ids)
        data['excell'] = self._get_picking_excell(picking_ids)
        # if data['pdf'] or data['excell']:
        #     raise models.ValidationError(_('Pdf and excell are not found!'))

        data['invoice_ids'] = self._get_invoice_create(picking_ids) # order_id
        data['mail'] = self._post_mail(data['picking_ids'], data['invoice_ids']) # return [True, True]

        pdf_attachment = data['pdf']
        excel_attachment = data['excell']

        # Zip oluştur
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr(pdf_attachment.name, base64.b64decode(pdf_attachment.datas))
            zf.writestr(excel_attachment.name, base64.b64decode(excel_attachment.datas))
        zip_buffer.seek(0)
        zip_file = base64.b64encode(zip_buffer.read())
        zip_filename = str(fields.Date.today()) + "_lieferungen.zip"

        zip_attachment = self.env['ir.attachment'].create({
            'name': zip_filename,
            'type': 'binary',
            'datas': zip_file.decode('utf-8'),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/zip',
        })

        # Tek URL ile download
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{zip_attachment.id}?download=true',
            'target': 'self',
        }
