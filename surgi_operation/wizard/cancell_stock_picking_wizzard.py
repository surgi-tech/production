from odoo import fields, models, api, exceptions
from odoo.exceptions import  Warning

# ------------- A.Salama -------------------
class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    # Method that responsable for to open wizard#
    def open_wizard_cancel_operation(self):
        action = self.env.ref('surgi_operation.action_cancel_sp_wizard_view')
        result = action.read()[0]
        res = self.env.ref('surgi_operation.cancel_sp_wizard_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result


class wizard_cancel_operation(models.TransientModel):
    _name = "wizard_cancel_stock_picking"

    # =============== wizard fields ================
    reason = fields.Many2one(comodel_name='operation.cancel.reason', string="Reason")
    description = fields.Text(string="Description")

    def wizard_cancell_operation(self):
        # print "LLLLLLLLLLLLLLLO$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        stock_pick_active_ids = self._context.get('active_ids')
        pick_ids = self.env['stock.picking'].browse(stock_pick_active_ids)
        pick_ids.action_cancel()
        pick_ids.write({
                'reason': self.reason.id,
                'description': self.description,
                'state':'cancel',
            })
        pick_ids.message_post(body="reason : %s <br/>description : %s"
                                   % (self.reason.name, self.description))
