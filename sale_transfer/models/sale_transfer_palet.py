from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_add_pallet_wizard(self):
        self.ensure_one()

        pallet_products = self.env['product.product'].browse(self.env.ref('l10n_data.product_palet').id).product_tmpl_id.product_variant_ids
        karton_products = self.env['product.product'].browse(self.env.ref('l10n_data.product_karton').id).product_tmpl_id.product_variant_ids

        product_ids = (pallet_products | karton_products).ids

        wizard = self.env['sale.transfer.package'].create({
            'sale_id': self.id,
            'package_line': [
                (0, 0, {
                    'product_id': move.product_id.id,
                    'qty': move.product_uom_qty,
                    'move_id': move.id,
                })
                for picking in self.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
                for move in picking.move_lines.filtered(
                    lambda m: m.product_id.id in product_ids
                )
            ],
        })

        # Open form
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Pallet',
            'res_model': 'sale.transfer.package',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
    # def action_open_add_pallet_wizard(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Add Pallet',
    #         'res_model': 'sale.transfer.package',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_sale_id': self.id,
    #         },
    #     }

    def action_open_delivery_form(self):
        self.ensure_one()
        pickings = self.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        if not pickings:
            raise UserError("No open delivery found for this sale order.")

        picking = pickings[0]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
            'target': 'new',
        }

    def name_get(self):
        result = super().name_get()
        name_dict = dict(result)

        if self.env.context.get('show_pallet_info'):
            for order in self:
                order_id = order.id
                plt_names = []
                if order.picking_ids:
                    picking = order.picking_ids.filtered(lambda l: l.state not in ('done', 'cancel'))
                    packet_move = picking.move_lines.filtered(lambda l: not l.sale_line_id)
                    for move in packet_move:
                        plt_names.append(f'[{move.product_uom_qty} > {move.product_id.default_code}]')

                if plt_names:
                    name_dict[order_id] = f"{name_dict[order_id]} {' '.join(plt_names)}"

        return [(rec_id, name) for rec_id, name in name_dict.items()]