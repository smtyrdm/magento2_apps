from odoo import models, fields, api, _
from collections import Counter

class SaleBatchTransferWiz(models.TransientModel):
    _inherit = 'sale.batch.transfer.wiz'

    def _get_picking_confirm(self, order_line):
        picking_ids = self.env['stock.picking']
        # Satırları sipariş bazlı grupla
        orders = order_line.mapped('order_id')
        for order in orders:
            lines = order_line.filtered(lambda l: l.order_id == order and l.qty_done > 0 and l.product_id.type in ['product', 'consu'])
            move_ids = lines.mapped('move_ids').filtered(lambda m: m.state not in ['done', 'cancel'] and m.picking_code == 'outgoing')
            if not move_ids:
                continue

            # Tek picking seç (o siparişin ortak picking'i olsun)
            picking = Counter(move.picking_id for move in move_ids).most_common(1)[0][0]
            move_ids.write({'picking_id': picking.id})

            # Seçili satırlar için qty_done dağıt
            for line in lines:
                # compute hesaplanı değil db deki getir.
                qty_done = line.with_context(manual_qty_done=True).qty_done

                for mov in move_ids.filtered(lambda m: m.sale_line_id.id == line.id):
                    if qty_done == 0:
                        mov.quantity_done = 0
                        continue
                    fark = mov.product_uom_qty - qty_done
                    if fark >= 0:
                        mov.quantity_done = line.qty_done
                        qty_done = 0
                    else:
                        mov.quantity_done = mov.product_uom_qty
                        qty_done = abs(fark)


            # Picking’i doğrula
            picking.with_context(skip_backorder=True).button_validate()
            picking_ids |= picking
        return picking_ids


