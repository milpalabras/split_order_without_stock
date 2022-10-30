# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SplitSale(models.TransientModel):
    _name = "sag.cancel_out_stock_wz"

    name = fields.Text(string="Nombre")    
    order = fields.Many2one('sale.order')

    def cancelar_sin_stock(self):
        sale_active_ids = self._context.get('active_ids', []) or []
        sale = self.env['sale.order'].browse(sale_active_ids)
        self.order = sale.id    
        #Recorremos todas las lineas de la orden de venta
        for line in self.order.order_line:            
            #Si la linea tiene no tiene stock, seteamos en cero y la anulamos en la entrega
            if line.virtual_available_at_date < line.qty_to_deliver and not line.is_mto:
                line.button_cancel_remaining() 
                  
        return 
                

        

    

