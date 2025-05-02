from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_combine_pickings(self):
        """
        Combina los remitos seleccionados en un nuevo remito de salida (tipo entrega)
        Agrupa todos los productos, cantidades, unidades de medida
        """
        pickings = self.browse(self.env.context.get('active_ids', []))
        
        if not pickings:
            raise UserError(_("Debe seleccionar al menos un remito para combinar."))
        
        # Verificar permisos
        if not self.env.user.has_group('stock.group_stock_user'):
            raise UserError(_("No tiene permisos para realizar esta acción."))
        
        # Obtener el tipo de operación de entrega (outgoing)
        outgoing_picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id', 'in', pickings.mapped('picking_type_id.warehouse_id').ids)
        ], limit=1)
        
        if not outgoing_picking_type:
            raise UserError(_("No se encontró un tipo de operación de entrega configurado."))
        
        # Verificar que todos los remitos tengan la misma ubicación de destino (cliente)
        dest_locations = pickings.mapped('location_dest_id')
        if len(dest_locations) > 1:
            raise UserError(_("No se pueden combinar remitos con diferentes ubicaciones de destino (clientes diferentes)."))
        
        # Verificar ubicaciones de origen (deben ser del mismo almacén)
        warehouses = pickings.mapped('location_id.warehouse_id')
        if len(warehouses) > 1:
            raise UserError(_("No se pueden combinar remitos de diferentes almacenes."))
        
        # Crear un nuevo remito de entrega (outgoing)
        new_picking = self.env['stock.picking'].create({
            'picking_type_id': outgoing_picking_type.id,
            'location_id': outgoing_picking_type.default_location_src_id.id,
            'location_dest_id': dest_locations.id,
            'origin': ', '.join(pickings.mapped('name')),
            'move_type': 'direct',
            'partner_id': pickings[0].partner_id.id if pickings[0].partner_id else False,
        })
        
        # Agrupar todas las líneas de los remitos seleccionados
        product_data = {}
        
        # Recorrer todos los movimientos de los remitos seleccionados
        for picking in pickings:
            for move in picking.move_ids_without_package:
                key = (move.product_id.id, move.product_uom.id)
                if key in product_data:
                    # Sumar cantidades si el producto ya existe
                    product_data[key]['product_uom_qty'] += move.product_uom_qty
                else:
                    # Crear nueva entrada para el producto
                    product_data[key] = {
                        'product_id': move.product_id.id,
                        'name': move.product_id.name + _(' (Combinado)'),
                        'product_uom_qty': move.product_uom_qty,
                        'product_uom': move.product_uom.id,
                        'location_id': outgoing_picking_type.default_location_src_id.id,
                        'location_dest_id': dest_locations.id,
                        'picking_id': new_picking.id,
                    }
        
        # Crear los movimientos en el nuevo remito
        for vals in product_data.values():
            self.env['stock.move'].create(vals)
        
        # Transferir automáticamente los productos si todos los remitos originales están listos
        if all(p.state == 'assigned' for p in pickings):
            new_picking.action_assign()
            if new_picking.state == 'assigned':
                new_picking.button_validate()
        
        # Abrir el nuevo remito creado
        return {
            'name': _('Remito de Entrega Combinado'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': new_picking.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }