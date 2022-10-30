# -*- coding:utf-8 -*-


{
    'name': 'Divisor de ordenes de venta sin stock',
    'version': '13.0',
    'depends': [
        'base','sale','purchase','operacion_logistica','sale_stock_ux'
    ],
    'author': 'Sergio Gomez',
    'website': 'http://www.milpalabras.com.ar',
    'summary': 'Modulo divisor de ordenes de venta sin stock',
    'category': 'Extra Tools',
    'description': '''
        Divide las ordenes de venta si el producto en las order lines no tiene stock, y anula ese producto en la entrega.
        Tambien agrega un boton para cancelar las lineas de la orden de venta que no tienen stock en la entrega.
    ''',
    'data': [
        'security/ir.model.access.csv',   
        'wizards/split_sale_wz_view.xml',    
        'wizards/cancel_out_stock_wz_view.xml',    
        'views/sale_order_inherit_view.xml',
        'views/cancel_out_stock_inherit_view.xml',
        
    ],
}