from odoo import models, api

class StockMove(models.Model):
    _inherit = 'stock.move'
    # üretim ise stock çıkışında üretim olaylansın.

    def _action_done(self, cancel_backorder=False):
        done_moves = super()._action_done(cancel_backorder=cancel_backorder)
        for move in done_moves.filtered(lambda l: l.picking_code == 'outgoing'): # delivery
            move = move.sudo()
            mrp = move.created_production_id or move.production_id or move.raw_material_production_id
            # Eğer mrp yoksa veya mrp var ama teslim edilen miktar sıfırsa
            if not move.quantity_done:
                continue
            if not mrp or mrp.state == 'done':
                continue
            if mrp.state == 'cancel':
                raise models.ValidationError(f"{mrp.name} Cancelled!")

            # ✅ Parçalı teslimat yoksa üretimi otomatik tamamla
            # ✅ Parçalı teslimat varsa ve adetler eşitse üretimi otomatik tamamla
            if not move.picking_id.backorder_ids or move.quantity_done == mrp.product_qty: # burda so da 2 adet gir sonrdan 2 adet attır buraya tek move mu geliyor bak.
                # Üretim miktarını stock move ile eşitle
                mrp.sudo().write({'qty_producing': move.quantity_done})
                mrp._set_qty_producing()
                mrp.sudo().with_context(skip_immediate=True).button_mark_done()
                #move.reserved_availability = move.quantity_done # üretim stock çıkışından sonra olduğu için sonradan rezerve edilmiş denilebilir.
                continue
            # parçalı teslimat ama satır adeti ile done adeti aynı
            if move.picking_id.backorder_ids and move.quantity_done == mrp.product_qty:
                # Üretim miktarını stock move ile eşitle
                mrp.sudo().write({'qty_producing': move.quantity_done})
                mrp._set_qty_producing()
                mrp.sudo().with_context(skip_immediate=True).button_mark_done()
                continue

            # ✅ Parçalı teslimat VARSA adetli
            name = mrp.name
            # 🔹 Yeni üretim oluştur (split)  [orijinal üretim miktarı, backorder miktarları]
            amounts = {mrp: [mrp.product_qty - move.quantity_done, move.quantity_done]}
            splitted = mrp._split_productions(amounts=amounts, cancel_remaning_qty=False, set_consumed_qty=False)
            new_mrp = (splitted - mrp) # mrp: (orjinal,backorder)
            # (WH/MO/00020-001:orjianl, WH/MO/00020-002:new)
            mrp.name = name # WH/MO/00020-001 > WH/MO/00020  (ÇOK ÖNEMLİ bunun ataması -002, -003, -004 gibi backorder olmasını sağlıyor.)


            # 🔹 Yeni üretimi move ile bağla
            move.created_production_id = new_mrp.id
            # 🔹 Yeni üretimi otomatik tamamla
            if new_mrp.product_qty == move.quantity_done:
                new_mrp.sudo().write({'qty_producing': move.quantity_done})
                new_mrp._set_qty_producing()
                new_mrp.sudo().with_context(skip_immediate=True).button_mark_done()
                #move.reserved_availability = move.quantity_done # üretim stock çıkışından sonra olduğu için sonradan rezerve edilmiş denilebilir.
            else:
                raise models.ValidationError(f"{mrp.name} Qty Producing Failed!")

        return done_moves