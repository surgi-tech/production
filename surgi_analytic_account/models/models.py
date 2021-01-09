from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    user_id = fields.Many2one(comodel_name="res.users", string="Salesperson",)
    user_add_ids = fields.Many2many(comodel_name="res.users",string="Additional Users", )


    salesteam_id = fields.Many2one(comodel_name="crm.team", string="Sales Team",)
    product_id = fields.Many2one(comodel_name="product.lines", string="Product Line",)
    undefined_sales_person = fields.Boolean(string="Undefined Sales Person",  )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_id = fields.Many2one(comodel_name="product.lines", string="Product Line",)

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_check = fields.Boolean(string="Check",  )

    # @api.onchange('is_check')
    def compute_analytic_account(self):

        analytic_account_obj=self.env['account.analytic.account'].search([])
        for line in self.invoice_line_ids:
            part=False
            for rec in analytic_account_obj:
                if line.product_id.product_id==rec.product_id:
                    part=True
                    if rec.user_id == self.invoice_user_id:
                        line.analytic_account_id=rec.id

                    elif self.invoice_user_id in rec.user_add_ids:
                        line.analytic_account_id = rec.id

                    elif rec.undefined_sales_person==True:
                        line.analytic_account_id = rec.id
                    else:
                        line.analytic_account_id=False
                if part==False:
                    line.analytic_account_id = False



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # name = fields.Char
    user_sales_id = fields.Many2one(comodel_name="res.users", string="Salesperson", required=False, )

    is_check = fields.Boolean(string="Check", )

    # @api.onchange('is_check')
    def compute_analytic_account(self):

        analytic_account_obj = self.env['account.analytic.account'].search([])
        for line in self.move_ids_without_package:
            part = False
            for rec in analytic_account_obj:
                if line.product_id.product_id == rec.product_id:
                    # part = True
                    if rec.user_id == self.user_sales_id:
                        line.analytic_account_id = rec.id
                        break

                    elif self.user_sales_id in rec.user_add_ids:
                        line.analytic_account_id = rec.id
                        break

                    elif rec.undefined_sales_person == True:
                        line.analytic_account_id = rec.id
                        break
                    else:
                        line.analytic_account_id = False
                        break
                else:
                    line.analytic_account_id = False
                    # break


# class StockMove(models.Model):
#     _inherit = 'stock.move'
#     analytic_account = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account",)

