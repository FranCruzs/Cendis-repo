{
    'name': 'Exportación de Remitos por Propietario',
    'version': '1.0',
    'summary': 'Permite exportar remitos seleccionados del mismo propietario',
    'description': """
        Agrega un botón para exportar remitos seleccionados a Excel,
        validando que todos pertenezcan al mismo propietario.
    """,
    'author': 'Tu Nombre',
    'website': 'https://tusitio.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}