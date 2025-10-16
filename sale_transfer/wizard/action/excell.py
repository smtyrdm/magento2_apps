from odoo import models, fields, api, _
import base64, csv, io
import logging
_logger = logging.getLogger(__name__)
class SaleBatchTransferWiz(models.TransientModel):
    _inherit = 'sale.batch.transfer.wiz'

    excel_file = fields.Binary("Excel File")
    excel_filename = fields.Char("Excel Filename")

    def _get_format_id(self,sale_id):
        phone = sale_id.partner_shipping_id.phone or sale_id.partner_id.phone or sale_id.partner_invoice_id.phone or ''
        format_id = f'46.{phone}'
        for partner in [sale_id.partner_id, sale_id.partner_id.parent_id, sale_id.partner_invoice_id,
                        sale_id.partner_invoice_id.parent_id]:
            if partner.company_name or partner.company_type == 'company':
                format_id = f'01.{phone}'
                break

        return format_id


    def _get_picking_excell(self, picking_ids, from_form=False):
        """Picking IDs ile CSV üretir ve wizard içinde tutar."""
        output = io.StringIO()
        writer = None

        for pckng in picking_ids:
            sale_id = pckng.sale_id
            format_id = self._get_format_id(sale_id)
            delivery = pckng.partner_id
            company = delivery.company_id
            reseller = delivery.parent_id
            
            if 'is_reseller' in delivery.parent_id._fields:
                reseller = delivery.parent_id.filtered(lambda l: l.is_reseller)

            row_data = {
                'AUFTRAGSDATUM': sale_id.date_order.strftime('%d.%m.%Y') if sale_id.date_order else '',
                'VMC': '',
                'VKDNR': sale_id.name or '',
                'VNAME1': company.name or '',
                'VSTRASSE': company.street or '',
                'VLAND': company.country_id.code or 'DEU',
                'VPLZ': company.zip or '',
                'VORT': company.city or '',
                'NEMAIL': reseller.email if reseller else '',
                'NLAND': reseller.country_id.code if reseller else 'DE',
                'NNAME1': reseller.name if reseller else '',
                'NORT': reseller.city if reseller else '',
                'NPLZ': reseller.zip if reseller else '',
                'NSTRASSE': reseller.street if reseller else '',
                'NTELNR': delivery.phone if reseller else '',
                'NUSTID': delivery.vat if reseller else '',
                'ENAME1': delivery.name or '',
                'ENAME2': '',
                'ESTRASSE': delivery.street or '',
                'ELAND': delivery.country_id.code or 'DE',
                'EPLZ': delivery.zip or '',
                'EORT': delivery.city or '',
                'EEMAIL': delivery.email or '',
                'ABHOLDATUMVON': '',
                'FRANKATUR': '30',
                'NACHNAHME': '',
                'WARENWERT': str(sale_id.amount_total).replace('.', ','),
                'SP1ANZAHL': "0",
                'SP1BREITE': "0",  # length,
                'SP1GEWICHT': "0",  # weight
                'SP1HOEHE': "0",  # widght,
                'SP1INHALT': 'Möbel',  # category
                'SP1LAENGE': "0",  # length,
                'SP1LIEFNR': pckng.name,
                'SP1MARK': '',
                'SP1VERP': 'EP',
                'HWT1': '01',
                'HWT1ART': 'I',
                'HWT1TEXT': delivery.phone,
                'HWT2': '51',
                'HWT2ART': 'I',
                'HWT2TEXT': '',
                **{f'HWT{i}': '' for i in range(3, 10)},
                **{f'HWT{i}ART': '' for i in range(3, 10)},
                **{f'HWT{i}TEXT': '' for i in range(3, 10)},
            }

            if writer is None:
                writer = csv.DictWriter(output, fieldnames=row_data.keys(), delimiter=';')
                writer.writeheader()
            writer.writerow(row_data)

        csv_data = '\ufeff' + output.getvalue()
        file_content = base64.b64encode(csv_data.encode('utf-8'))
        file_name = f"{fields.Date.today()}_lieferungen.csv"

        # Wizard içerisine kaydet
        self.excel_file = file_content
        self.excel_filename = file_name

        attachment = self.env['ir.attachment'].create({
            'name': self.excel_filename,
            'type': 'binary',
            'datas': self.excel_file.decode('utf-8'),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/csv',
        })

        return attachment

        #return {'excel_file': self.excel_file, 'excel_filename': self.excel_filename}


