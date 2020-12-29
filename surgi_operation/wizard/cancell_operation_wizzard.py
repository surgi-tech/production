from odoo import fields, models, api, exceptions
from odoo.exceptions import  Warning

# ------------- A.Salama -------------------
class operation_operation_inherit(models.Model):
    _inherit = 'operation.operation'

    # Method that responsable for to open wizard#
    def open_wizard_cancel_operation(self):
        print ("herrrrrrrrrrrrrrrrrrrrrrrrrre")
        action = self.env.ref('surgi_operation.action_cancel_wizard_view')
        result = action.read()[0]
        res = self.env.ref('surgi_operation.cancel_wizard_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result


class wizard_cancel_operation(models.TransientModel):
    _name = "wizard_cancel_operation"

    # =============== wizard fields ================
    reason = fields.Many2one(comodel_name='operation.cancel.reason', string="Reason")
    description = fields.Text(string="Description")

    def wizard_cancell_operation(self):
        operation_active_ids = self._context.get('active_ids')
        operation_ids = self.env['operation.operation'].browse(operation_active_ids)
        operation_ids.write({
                'reason': self.reason.id,
                'description': self.description,
                'state':'cancel',
            })
        for operation in operation_ids:
            operation.message_post(body="Cancelation Reason :<br/>Reason : %s <br/>Description : %s"
                                      % (self.reason.name, self.description))
        operation_ids.message_post(body="reason : %s <br/>description : %s"
                                   % (self.reason.name, self.description))
        stock_pickings_ids = self.env['stock.picking'].search([('operation_id', 'in', operation_active_ids)])
        if stock_pickings_ids:
            stock_pickings_ids.action_cancel()
            stock_pickings_ids.write({
                'reason': self.reason.id,
                'description': self.description,
            })
            for picking in stock_pickings_ids:
                picking.message_post(body="Cancelation Reason :<br/>Reason : %s <br/>Description : %s"
                               % (self.reason.name, self.description))

    def wizard_stock_cancell_operation(self):
        stock_active_ids = self._context.get('active_ids')
        stock_ids = self.env['operation.operation'].browse(stock_active_ids)
        stock_ids.action_cancel()
        stock_ids.write({
            'reason': self.reason.id,
            'description': self.description,
        })
        for picking in stock_ids:
            picking.message_post(body="Cancelation Reason :<br/>Reason : %s <br/>Description : %s"
                                      % (self.reason.name, self.description))