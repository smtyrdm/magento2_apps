from odoo import models, fields, api, _

class SaleBatchTransferWiz(models.TransientModel):
    _inherit = 'sale.batch.transfer.wiz'

    email = fields.Boolean(string='Send by Email', default=True)

    def _post_mail(self, picking_ids=None, invoice_ids=None):
        if not self.email:
            return

        if picking_ids:
            for pckg in picking_ids:
                if pckg.state != 'done':
                    continue

                template = self.env.ref('stock.mail_template_data_delivery_confirmation', raise_if_not_found=False)
                if template:
                    pckg.with_context(lang=pckg.partner_id.lang).message_post_with_template(
                        template.id,
                        email_layout_xmlid='mail.mail_notification_light',
                    )

        if invoice_ids:
            for inv in invoice_ids:
                if inv.state != 'posted':
                    continue

                template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
                if template:
                    inv.with_context(lang=inv.partner_id.lang).message_post_with_template(
                        template.id,
                        email_layout_xmlid='mail.mail_notification_light',
                    )
