# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    qty_done = fields.Float(string="Done Qty", compute='_compute_qty_done', store=True)
    transfer_time = fields.Datetime(related="order_id.commitment_date", string="Time", store=True)
    transfer_state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ('dropship', 'Dropship'),
    ], compute="_compute_transfer_state", store=True, string="Transfer")

    product_categ_id = fields.Many2one(comodel_name="product.category", related="product_id.categ_id", store=True, string="Product Category")


    @api.model
    def create(self, vals): # stock pickingde palet veya karton eklendiğinde sale line da ekleme yapmıyor.
        if vals.get('move_ids') and vals.get('product_id'):
            pallet_products = self.env['product.product'].browse(self.env.ref('l10n_data.product_palet').id).product_tmpl_id.product_variant_ids
            karton_products = self.env['product.product'].browse(self.env.ref('l10n_data.product_karton').id).product_tmpl_id.product_variant_ids
            product_ids = (pallet_products | karton_products).ids

            if vals['product_id'] in product_ids:
                return self.browse()

        return super().create(vals)

    @api.depends('move_ids','move_ids.state','purchase_line_ids','product_uom_qty', 'qty_delivered')
    def _compute_transfer_state(self):
        for line in self:
            if line.purchase_line_ids:
                line.transfer_state = 'dropship'
                continue
            move =  line.move_ids.mapped('state') or []
            for state in ['draft', 'waiting', 'confirmed','partially_available','assigned','cancel','done']:
                if state in move:
                    line.transfer_state = state
                    break
            else:
                line.transfer_state = False

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        for line in self:
            if 'qty_done' in vals and vals['qty_done'] > (line.product_uom_qty - line.qty_delivered):
                raise UserError(_("Done Quantity cannot be greater than remaining quantity!"))
        return res

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_qty_done(self):
        for line in self:
            # Eğer kullanıcı manuel değişim yaptıysa compute yapma
            if line.env.context.get('manual_qty_done'):
                continue
            line.qty_done = line.product_uom_qty - line.qty_delivered

    def action_sale_transfer(self):
        return {
            'name': _('Sale Transfer'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.batch.transfer.wiz',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids},
        }