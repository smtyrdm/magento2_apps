from odoo import models, fields, api, _


class SaleBatchTransferWiz(models.TransientModel):
    _inherit = 'sale.batch.transfer.wiz'

    invoice = fields.Boolean(string='Create Invoice', default=True)

    def _get_invoice_create(self, picking_ids):
        if not self.invoice:
            return
        invoice_ids = []
        order_ids = picking_ids.mapped('sale_id')
        for order in order_ids:
            # Wizard için context hazırla
            ctx = dict(self.env.context or {})
            ctx.update({'active_model': 'sale.order', 'active_ids': [order.id], 'active_id': order.id, 'lang': order.partner_id.lang})
            # Wizard instance, context ile
            wizard = self.env['sale.advance.payment.inv'].with_context(ctx).create({
                # Bu alanları default_get ile otomatik set edebiliriz, --> l10n_data/wizard/sale_make_invoice_advance.py
                # ama istersen burada da manuel set edebilirsin
            })
            if not order.invoice_ids:
                # Wizard açılmış gibi create_invoices çağır
                wizard.create_invoices()
            elif order.invoice_status != 'invoiced':  # parçalı
                wizard.create_invoices()

            for inv in order.invoice_ids:
                if inv.state == 'cancel':
                    continue
                if inv.state == 'draft':
                    inv.action_post()
                invoice_ids.append(inv)
        return invoice_ids

    # if self.invoice:
    #     invoice_ids = order_ids.get_invoice_create()
    # else:
    #     invoice_ids = []
