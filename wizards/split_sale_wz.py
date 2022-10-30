# -*- coding: utf-8 -*-


from email.policy import default
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SplitSale(models.TransientModel):
    _name = "sag.split_sale_wz"

    name = fields.Text(string="Nombre")
    split_sale_line_ids = fields.One2many('sag.split_sale_wz.line', 'split_sale_wz_id', string='Lineas')
    order = fields.Many2one('sale.order')
    

    def ver_productos_sin_stock(self):
        lines = []
        #mostramos todos los productos en la orden de venta y marcamos los que no tienen stock        
        sale_active_ids = self._context.get('active_ids', []) or []
        sale = self.env['sale.order'].browse(sale_active_ids)
        self.order = sale.id            
        for line in self.order.order_line:
            if line.virtual_available_at_date < line.qty_to_deliver and not line.is_mto:            
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_packaging_qty': line.product_packaging_qty,
                    'falta_stock': True,
                    
                }))
        if len(lines) > 0:
            self.split_sale_line_ids = False
            self.split_sale_line_ids = lines
            self.hide_button = False
            return{
                        'context': self.env.context,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'sag.split_sale_wz',
                        'res_id': self.id,
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
        else:
            raise ValidationError("No hay productos sin stock")
            


    def confirmar_separar_pendientes(self):
        #Guardamos lineas de descuento en el caso de que haya para usarlos en la nueva orden de venta
        sale_active_ids = self._context.get('active_ids', []) or []
        sale = self.env['sale.order'].browse(sale_active_ids)
        self.order = sale.id

        lineas_descuento = []
        for line_desc in self.order.linea_descuento:
            lineas_descuento.append((0,0,{'descuento': line_desc.descuento,
                                            'descuento_real': line_desc.descuento_real,
                                            'currency_id': line_desc.currency_id.id,
                                            'total_desc': line_desc.total_desc}))
        #Recorremos todas las lineas de la orden de venta y separamos productos con stock y sin stock
        products_out_stock = []
        product_with_stock = []        
        for line in self.order.order_line:            
            if line.virtual_available_at_date < line.qty_to_deliver and not line.is_mto:
                products_out_stock.append((0,0,{'product_id': line.product_id.id,
                                                'product_uom_qty': line.product_uom_qty,
                                                'product_packaging_qty': line.product_packaging_qty,
                                                'product_packaging': line.product_packaging.id,
                                                'qty_delivered': line.qty_delivered,
                                                'quantity_returned': line.quantity_returned,
                                                'qty_invoiced': line.qty_invoiced,
                                                'price_unit_package': line.price_unit_package,
                                                'price_unit': line.price_unit,                                                
                                                }))            
            else:
                product_with_stock.append((0,0,{'product_id': line.product_id.id,
                                                'product_uom_qty': line.product_uom_qty,
                                                'product_packaging_qty': line.product_packaging_qty,
                                                'product_packaging': line.product_packaging.id,
                                                'qty_delivered': line.qty_delivered,
                                                'quantity_returned': line.quantity_returned,
                                                'qty_invoiced': line.qty_invoiced,
                                                'price_unit_package': line.price_unit_package,
                                                'price_unit': line.price_unit,                                                
                                                }))
        
            #Si la linea no tiene stock, seteamos en cero y la anulamos en la entrega
            #(la funcion button_cancel_remaining() esta en el modulo sale_stock_ux)
        for line in self.order.order_line:
            if line.virtual_available_at_date < line.qty_to_deliver and not line.is_mto:
                line.button_cancel_remaining()                    
                
            
            # Verificamos que la lista de productos sin stock no este vacia
        if len(products_out_stock) > 0:
            #Creamos una nueva orden de venta con los productos sin stock               
            self.env['sale.order'].create({
                'partner_id': self.order.partner_id.id,
                'state': 'sale',
                'previsional': self.order.previsional,
                'operacion': self.order.operacion,
                'pricelist_id': self.order.pricelist_id.id,
                'journal_id': self.order.journal_id.id,
                'order_line': products_out_stock,                    
                'warehouse_id': self.order.warehouse_id.id,
                'talonario': self.order.talonario,
                'nroped': self.order.nroped,
                'linea_descuento': lineas_descuento,
            })
        else:
            raise ValidationError("No hay productos sin stock")
        
        return

class SaleOrderLine(models.TransientModel):
    _name = 'sag.split_sale_wz.line'

    split_sale_wz_id = fields.Many2one('sag.split_sale_wz', string='Split Sale Id', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    product_uom_qty = fields.Float(string='Cantidad')
    product_packaging_qty = fields.Float(string='cantidad de paquetes')
    falta_stock = fields.Boolean(string='Falta stock', default=False)
