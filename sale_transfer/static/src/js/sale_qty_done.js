odoo.define('sale_batch_transfer.sale_qty_done', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    const QtyDoneWidget = AbstractField.extend({
        supportedFieldTypes: ['float', 'integer'],

        _render: function () {
            this.$el.empty();

            const qtyDone = this.value || 0;
            const qtyReceived = this.recordData.qty_delivered || 0;
            const productQty = this.recordData.product_uom_qty || 0;

            const minVal = -qtyReceived;
            const maxVal = productQty - qtyReceived;

            const $input = $('<input>', {
                type: 'number',
                value: qtyDone,
                min: minVal,
                max: maxVal,
                step: 'any',
                class: 'o_input o_field_number',
                css: {
                    height: '32px',   // yükseklik
                    lineHeight: '32px',
                    width: '55px',
                    fontSize: '14px',
                    fontWeight: 'bold',
                },
            });

            // Elle yazmayı engelle
            $input.on('keydown', (ev) => {
                ev.preventDefault();  // klavyeden yazmayı engelle
            });


            $input.on('click', (ev) => {
                ev.stopPropagation();   // satır seçilmesini engelle
            });

            // Anlık DB write
            $input.on('change', (ev) => {
                ev.stopPropagation();   // satır eventlerine gitmesin
                const newVal = parseFloat(ev.target.value) || 0;

                this._rpc({
                    model: this.model,                  // örn. purchase.order.line
                    method: 'write',
                    args: [[this.res_id], {qty_done: newVal}],
                }).then(() => {
                    this._setValue(newVal); // UI'de de güncelle
                });
            });

            this.$el.append($input);
        },
    });

    fieldRegistry.add('sale_qty_done', QtyDoneWidget);

    return QtyDoneWidget;
});
