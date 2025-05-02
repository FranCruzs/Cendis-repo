{
    'name': 'Destino en Albaranes',
    'version': '1.0',
    'summary': 'Añade campo destino a los albaranes',
    'description': '''
    Este módulo añade un campo de selección "Destino" a los albaranes (stock.picking)
    ''',
    'author': 'Tu Nombre',
    'website': 'https://tusitio.com',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}