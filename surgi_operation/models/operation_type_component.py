from odoo import fields,models,api
from odoo.fields import Datetime
from odoo.exceptions import Warning

class surgitech_product_operation_type(models.Model):
    _name = 'product.operation.type'
    _inherit = ['mail.thread']

    name = fields.Char(string="Operation Type",track_visibility=True)
    operation_type_category = fields.Char(string="Category", required=False, )
    operation_product_line = fields.Char(string="Product Line", required=False, )
    invoice_printing_description = fields.Text('Invoice Printing Description')

class surgitech_product(models.Model):
    _inherit = 'product.template'

    operation_component = fields.Boolean(string="Is Operation Component")
    #operation_type = fields.Many2one('product.operation.type',string="Operation Type")
    is_medical = fields.Boolean(string="Is Medical",default=False)
    is_tool = fields.Boolean(string="Is Tool",default=False)
    is_op_acc = fields.Boolean(string="Is Accessory",default=False)
    operation_type = fields.Many2many(comodel_name="product.operation.type",
    relation="product_operation_type_product_template_rel",
                                      column1="product_template_id",
                                      column2="product_operation_type_id", string="Operation Type" )

    tool_line_ids = fields.One2many(
        comodel_name='product.tool.line',
        inverse_name='product_id',
        string='Tools',
        help='List of Tools where product is used.'
    )


#class surgitech_product_product(models.Model):
#    _inherit = 'product.template'

    #operation_component = fields.Boolean(string="Is Operation Component")
    #operation_type = fields.Many2one('product.operation.type',string="Operation Type")



