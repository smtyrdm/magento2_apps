from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleTransferPackage(models.TransientModel):
    _name = "sale.transfer.package"
    _description = "Sale Transfer Package"

    sale_id = fields.Many2one("sale.order", string="Sale Order")
    package_line = fields.One2many('sale.transfer.package.line', 'package_id', string="Package Lines")

    def action_add_pallet(self):
        self.ensure_one()
        picking = self.sale_id.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        if not picking:
            raise UserError("No open delivery found for this sale order. Please create a delivery first.")
        if len(picking) > 1:
            raise UserError("Only one picking can be added to this sale order.")

        picking = picking[0]

        for line in self.package_line:
            if not line.move_id:
                move = self.env["stock.move"].create({
                    "picking_id": picking.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty,
                    "quantity_done": line.qty,
                    "product_uom": line.product_id.uom_id.id,
                    "name": line.product_id.name,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                    "sale_line_id": False,
                })
                move._action_confirm()
                move._action_assign()

                line.move_id = move

            else:
                line.move_id.product_uom_qty = line.qty
                line.move_id.product_id = line.product_id
                line.move_id._action_assign()

        return {"type": "ir.actions.act_window_close"}


class SaleTransferPackageLine(models.TransientModel):
    _name = "sale.transfer.package.line"
    _description = "Sale Transfer Package Lines"

    package_id = fields.Many2one('sale.transfer.package', string="Package", required=True, ondelete='cascade')

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain=lambda self: self._get_product_domain(),
    )
    qty = fields.Float(string="Qty", required=True, default=1.0)
    move_id = fields.Many2one('stock.move')
    picking_id = fields.Many2one(related="move_id.picking_id", string="Picking")

    @api.model
    def _get_product_domain(self):

        pallet_products = self.env['product.product'].browse(
            self.env.ref('l10n_data.product_palet').id
        ).product_tmpl_id.product_variant_ids
        karton_products = self.env['product.product'].browse(
            self.env.ref('l10n_data.product_karton').id
        ).product_tmpl_id.product_variant_ids
        product_ids = (pallet_products | karton_products).ids
        domain = [('id', 'in', product_ids)]

        return domain

    def unlink(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.write({"state": "draft"})
                rec.move_id.sudo().unlink()
        return super(SaleTransferPackageLine, self).unlink()


        # @api.model
        # def default_get(self, fields):
        #     res = super().default_get(fields)
        #     sale_id = self._context.get('default_sale_id')
        #     if sale_id:
        #         sale = self.env['sale.order'].browse(sale_id)
        #         # Mevcut palet ürünlerini al
        #         package_lines = []
        #         picking = sale.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        #         if picking:
        #             picking = picking[0]
        #             for move in picking.move_lines.filtered(lambda m: m.product_id.product_tmpl_id.variant_code == 'PLT' or m.product_id.product_tmpl_id.default_code == 'PLT'):
        #                 package_lines.append((0, 0, {
        #                     'product_id': move.product_id.id,
        #                     'qty': move.product_uom_qty,
        #                     'move_id': move.id,
        #                 }))
        #         res['package_line'] = package_lines
        #     return res



        # self.ensure_one()
        # picking = self.sale_id.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        # if not picking:
        #     raise UserError("No open delivery found for this sale order. Please create a delivery first.")
        # if len(picking) > 1:
        #     raise UserError("Only one picking can be added to this sale order.")
        #
        # picking = picking
        #
        # picking.move_lines.filtered(lambda m: m.product_id.product_tmpl_id.variant_code == 'PLT' or m.product_id.product_tmpl_id.default_code == 'PLT').unlink()
        #
        #
        #
        # for line in self.package_line:
        #     self.env['stock.move'].create({
        #         'picking_id': picking.id,
        #         'product_id': line.product_id.id,
        #         'product_uom_qty': line.qty,
        #         'product_uom': line.product_id.uom_id.id,
        #         'name': line.product_id.name,
        #         'location_id': picking.location_id.id,
        #         'location_dest_id': picking.location_dest_id.id,
        #         'sale_line_id': False,
        #     })
        #
        # return {'type': 'ir.actions.act_window_close'}



# class SaleTransferPallet(models.TransientModel):
#     _name = "sale.transfer.pallet"
#     _description = "Add Palet to Delivery"
#
#
#     sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=True)
#     pallet_product_id = fields.Many2one("product.product", string="Pallet", required=True, domain=["|",("product_tmpl_id.variant_code", "=", "PLT"),("product_tmpl_id.default_code", "=", "PLT")])
#     qty = fields.Float(string="Quantity", required=True, default=1.0)
#
#     def action_add_pallet(self):
#         self.ensure_one()
#         picking = self.sale_order_id.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
#         if not picking:
#             raise UserError("No open delivery found for this sale order. Please create a delivery first.")
#
#         picking = picking[0]
#
#         self.env['stock.move'].create({
#             'picking_id': picking.id,
#             'product_id': self.pallet_product_id.id,
#             'product_uom_qty': self.qty,
#             'product_uom': self.pallet_product_id.uom_id.id,
#             'name': self.pallet_product_id.name,
#             'location_id': picking.location_id.id,
#             'location_dest_id': picking.location_dest_id.id,
#             'sale_line_id': False,
#         })
#
#         return {'type': 'ir.actions.act_window_close'}