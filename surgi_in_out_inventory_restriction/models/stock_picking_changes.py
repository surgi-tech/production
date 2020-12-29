from odoo import fields,models,api

class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'
    # ======================= A.Salama =====================

    # method used to tread picking type code
    @api.depends('picking_type_id')
    def get_picking_type_code(self):
        for rec in self:
            rec.picking_type_code_new = rec.picking_type_id.code

    # add field to compute picking type code
    picking_type_code_new = fields.Char(string="Picking Type Code",compute=get_picking_type_code)

    def is_valid_show(self):
        pick_type = self.picking_type_id.code
        if pick_type == 'internal':
            self.is_valid = True

        elif pick_type == 'incoming' and self.env.user.has_group('surgi_in_out_inventory_restriction.validate_in_group'):
            self.is_valid = True

        elif pick_type == 'outgoing' and self.env.user.has_group('surgi_in_out_inventory_restriction.validate_out_group'):
            self.is_valid = True
        else:
            self.is_valid = False

    is_valid = fields.Boolean(string="Validation Availability",compute='is_valid_show')

