{
    'name': 'Sale Transfer',
    'version': '15.0.0.1.0',
    'category': 'Sale',
    # sale_invoice_percent > bu sale da fatura üretirken % ise %50 ödeme yöntemi misal.
    # stock_picking_send_by_mail > irsaliye mail oca nın
    "depends": ["sale","stock","mrp"],
    'data': [
        'security/ir.model.access.csv',
        'data/server_actions.xml',
        "views/sale_views.xml",
        "wizard/transfer.xml",
        "wizard/transfer_package.xml",
    ],
    'assets': {
        "web.assets_backend": [
            "sale_transfer/static/src/**/*",
        ],
    },
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}


