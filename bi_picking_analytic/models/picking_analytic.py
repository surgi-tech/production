# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import datetime
from collections import namedtuple, OrderedDict, defaultdict


class ProcurementRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'pull' or 'pull_push') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        group_id = False
        if self.group_propagation_option == 'propagate':
            group_id = values.get('group_id', False) and values['group_id'].id
        elif self.group_propagation_option == 'fixed':
            group_id = self.group_id.id

        date_expected = fields.Datetime.to_string(
            fields.Datetime.from_string(values['date_planned']) - relativedelta(days=self.delay or 0)
        )
        # it is possible that we've already got some move done, so check for the done qty and create
        # a new move with the correct qty
        qty_left = product_qty
        move_values = {
            'name': name[:2000],
            'company_id': self.company_id.id or self.location_src_id.company_id.id or self.location_id.company_id.id or company_id.id,
            'product_id': product_id.id,
            'product_uom': product_uom.id,
            'product_uom_qty': qty_left,
            'partner_id': self.partner_address_id.id or (values.get('group_id', False) and values['group_id'].partner_id.id) or False,
            'location_id': self.location_src_id.id,
            'location_dest_id': location_id.id,
            'move_dest_ids': values.get('move_dest_ids', False) and [(4, x.id) for x in values['move_dest_ids']] or [],
            'rule_id': self.id,
            'procure_method': self.procure_method,
            'origin': origin,
            'picking_type_id': self.picking_type_id.id,
            'group_id': group_id,
            'route_ids': [(4, route.id) for route in values.get('route_ids', [])],
            'warehouse_id': self.propagate_warehouse_id.id or self.warehouse_id.id,
            'date': date_expected,
            'date_expected': date_expected,
            'propagate_cancel': self.propagate_cancel,
            'propagate_date': self.propagate_date,
            'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
            'description_picking': product_id._get_description(self.picking_type_id),
            'priority': values.get('priority', "1"),
            'delay_alert': self.delay_alert,
            'analytic_account_id': values.get('analytic_account_id', 0),
            'tag_ids': values.get('tag_ids', 0),
        }
        for field in self._get_custom_move_fields():
            if field in values:
                move_values[field] = values.get(field)
        return move_values

    # def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name,values,origin,group_id,company_id):
    #     move_values = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, group_id, company_id)
    #
    #     move_values.update({
    #         'analytic_account_id':values('analytic_account_id',0),
    #         'tag_ids':values.get('tag_ids',0),
    #
    #         })
    #     return move_values


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self,group_id):
        res = super(SaleOrderLine,self)._prepare_procurement_values(group_id=group_id)
        tag_ids = []
        for tag in self.analytic_tag_ids:
            tag_ids.append(tag.id)
        res.update({
            'analytic_account_id':self.order_id.analytic_account_id.id,
            'tag_ids':[(6,0,tag_ids)],
            })
        return res

class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        tag_ids = []
        for tag in self.analytic_tag_ids:
            tag_ids.append(tag.id)
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'analytic_account_id':self.account_analytic_id.id,
            'tag_ids':[(6,0,tag_ids)],
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if self.product_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = diff_quantity
            res.append(template)
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    tag_ids  = fields.Many2many('account.analytic.tag', string= 'Tag')


    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
        # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        rslt={}
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",debit_account_id,credit_account_id)

        self.ensure_one()
        if self._context.get('forced_ref'):
            ref = self._context['forced_ref']
        else:
            ref = self.picking_id.name

        tag_ids = []
        for tag in self.tag_ids:
            tag_ids.append(tag.id)

        if self.picking_id.picking_type_id.receipt_exchange==True:
            cridite_value=self.product_id.categ_id.property_stock_account_output_categ_id.id
        else:
            cridite_value=credit_account_id

        debit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            'analytic_account_id':self.analytic_account_id.id,
            'analytic_tag_ids': [(6,0,tag_ids)],
        }

        debit_line_vals22 = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'analytic_tag_ids': [(6, 0, tag_ids)],
        }

        credit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': cridite_value,
        ### Hashed by Mostafa Nassar ###
            # 'analytic_account_id':self.analytic_account_id.id,
            # 'analytic_tag_ids': [(6,0,tag_ids)],
        }
        credit_line_vals22 = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': cridite_value,
            'analytic_account_id':self.analytic_account_id.id,
            'analytic_tag_ids': [(6,0,tag_ids)],
        }

        if self.picking_id.picking_type_id.code=='outgoing':
            rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if self.picking_id.picking_type_id.code=='incoming':
            rslt = {'credit_line_vals': credit_line_vals22, 'debit_line_vals': debit_line_vals22}

        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):

        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        if self._context.get('force_valuation_amount'):
            valuation_amount = self._context.get('force_valuation_amount')
        else:
            valuation_amount = cost

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount)

        # check that all data is correct
        if self.company_id.currency_id.is_zero(debit_value) and not self.env['ir.config_parameter'].sudo().get_param('stock_account.allow_zero_cost'):
            raise UserError(_("The cost of %s is currently equal to 0. Change the cost or the configuration of your product to avoid an incorrect valuation.") % (self.product_id.display_name,))
        credit_value = debit_value


        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]
        return res



class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        sale_list=[]
        ref = self.name
        sale_analytic_dict={}
        purchase_analytic_dict={}
        if self.sale_id :
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                    tag_ids = []
                    for tag_id in line.tag_ids:
                        tag_ids.append(tag_id.id)
                    sale_analytic_dict.update({
						'name': line.sale_line_id.product_id.name,
						'amount': line.sale_line_id.price_unit,
		                                'product_id': line.sale_line_id.product_id.id,
						'product_uom_id': line.sale_line_id.product_uom.id,
						'date': line.date_expected,
						'account_id': line.analytic_account_id.id,
						'unit_amount': line.quantity_done,
						'general_account_id': self.partner_id.property_account_receivable_id.id,
						'ref': ref,
                                                'tag_ids':[(6,0,tag_ids)]
			        })
                    self.env['account.analytic.line'].create(sale_analytic_dict)

        if self.purchase_id :
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                   tag_ids = []
                   for tag_id in line.tag_ids:
                        tag_ids.append(tag_id.id)

                   purchase_analytic_dict.update({
						'name': line.purchase_line_id.product_id.name,
						'date': line.date_expected,
						'account_id': line.analytic_account_id.id,
						'unit_amount': line.quantity_done,
						'amount': (line.product_id.standard_price *line.quantity_done) * -1,
						'product_id': line.purchase_line_id.product_id.id,
						'product_uom_id': line.purchase_line_id.product_uom.id,
						'general_account_id': self.partner_id.property_account_payable_id.id,
						'ref': ref,
                                                'tag_ids':[(6,0,tag_ids)]
					})

                   self.env['account.analytic.line'].create(purchase_analytic_dict)


        if not self.purchase_id and not self.sale_id:
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                   tag_ids =[]
                   for tag_id in line.tag_ids:
                        tag_ids.append(tag_id.id)

                   purchase_analytic_dict.update({

						'name': line.product_id.name,
						'date': datetime.now(),
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity_done ,
                        'amount': line.product_id.lst_price * line.quantity_done ,
                        'product_id': line.product_id.id,
						'product_uom_id': line.product_uom.id,
                        'general_account_id': self.partner_id.property_account_receivable_id.id,
						'ref': ref,
                        'tag_ids':[(6,0,tag_ids)]
					})
                   if self.picking_type_id.code == 'incoming':
                       purchase_analytic_dict['amount']= (line.product_id.standard_price *line.quantity_done) * -1

                   self.env['account.analytic.line'].create(purchase_analytic_dict)
        return super(StockPicking, self).button_validate()



