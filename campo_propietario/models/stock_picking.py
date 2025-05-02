from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    x_studio_propietario = fields.Many2one(
        'res.partner',
        string='Propietario',
        compute='_compute_propietario',
        store=True,
        readonly=True,
    )
    
    destino_id = fields.Many2one(
        'res.partner',
        string='Contacto de Entrega',
        compute='_compute_destino_id',
        inverse='_inverse_destino_id',
        store=True,
        readonly=False,
        domain="[('parent_id', '=', x_studio_propietario)]",
    )
    
    @api.depends('owner_id')
    def _compute_propietario(self):
        for picking in self:
            picking.x_studio_propietario = picking.owner_id
    
    @api.depends('x_studio_propietario')
    def _compute_destino_id(self):
        for picking in self:
            if not picking.x_studio_propietario:
                picking.destino_id = False
                continue
                
            # Buscar SOLO los hijos directos (excluyendo al propietario)
            child_contacts = self.env['res.partner'].search([
                ('parent_id', '=', picking.x_studio_propietario.id),
                ('id', '!=', picking.x_studio_propietario.id),
            ])
            
            # Resetear si el destino actual no es un hijo válido
            if picking.destino_id and picking.destino_id not in child_contacts:
                picking.destino_id = False
            
            # Opcional: Auto-seleccionar el primer hijo si no hay selección
            if not picking.destino_id and child_contacts:
                picking.destino_id = child_contacts[0]
    
    def _inverse_destino_id(self):
        """Permite guardar manualmente el valor"""
        pass
    
    @api.onchange('x_studio_propietario')
    def _onchange_propietario(self):
        if not self.x_studio_propietario:
            self.destino_id = False
            return {
                'domain': {'destino_id': [('id', '=', -1)]}  # Bloquear selección
            }
        
        # Forzar el dominio en el Many2one
        return {
            'domain': {
                'destino_id': [
                    ('parent_id', '=', self.x_studio_propietario.id),
                    ('id', '!=', self.x_studio_propietario.id),
                ]
            },
        }