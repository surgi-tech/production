# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning

## A.Salama .... Code Start
class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'


    receipt_exchange = fields.Boolean(string="Receipt Exchange? ",related='picking_type_id.receipt_exchange',
                                      help="Used ot show if type is receipt exchange or not")
    # delivery_exchange = fields.Boolean(string="Delivery Exchange",tracking=True,
    #                                   help="Used ot show if type is receipt exchange or not")
    so_delivery_type = fields.Selection(string="Delivery Type ", related='sale_id.delivery_type',
                                        selection=[('normal', 'Normal')
                                            , ('delivery2customer', 'Delivery To Customer')
                                            , ('delivery2tender', 'Delivery To Tender')
                                            , ('deliveryorder', 'Delivery Order')
                                            , ('loading', 'Loading')
                                            , ('deliveryexchange', 'Delivery Exchange')
                                            , ('deliveryreplacement', 'Delivery Replacement')
                                            , ('purchasereturn', 'Purchase Return')
                                            , ('gov', 'Government Form')],
                                        help="Used ot show picking type delivery type")
    inv_receipt_type = fields.Selection(string="Receipt Type ",
                                        selection=[('receipt4vendor', 'Receipt From Vendor')
                                            , ('receipt4tender', 'Receipt From Tender')
                                            , ('receiptexchange', 'Receipt Exchange')
                                            , ('saletreturn', 'Sales Return')
                                            , ('receiptreplacement', 'Delivery Replacement')],
                                        help="Used ot show picking type Receipt type")
    delivery_exchange_order_id = fields.Many2one(comodel_name='stock.picking',string="Exchange Delivery Order",
                             help="used to set Tender Delivery Order",
                                      domain=[('so_delivery_type','=','exchange')])
    receipt_exchange_order_id = fields.Many2one(comodel_name='stock.picking', string="Exchange Receipt Order",
                                      help="used to set Exchange Receipt Order",
                                      domain=[('receipt_exchange', '=', True)])
    gov_form_url = fields.Char(string="Gov Form URL",help="used to add Gov Form URL")

    approval_lines=fields.One2many('approval.line','pick_id')

    total_cocs = fields.Float(string="Total Cocs",store=True,)#compute='_compute_total_cocs'
    sales_order_id = fields.Many2one(comodel_name="sale.order", string="Original Sale Order", required=False, )
    # sales_person_id = fields.Many2one(comodel_name="res.users", string="SalesPerson",), required=False, readonly="1"
    is_exchange = fields.Boolean(string="",compute='_cumpute_is_exchange' )

    sale_id = fields.Many2one(related="group_id.sale_id", string="Sales Order", store=True,
                              readonly=False, tracking=True)
    user_sales_id = fields.Many2one(comodel_name="res.users",related="sale_id.user_id",  string="Salesperson")

    check_exchange = fields.Boolean(string="Exchange Status",compute='check_is_exchange')


    state_delivery = fields.Boolean(string="",compute='change_state_delivery'  )
    @api.depends('sale_id')
    def change_state_delivery(self):
        self.state_delivery=False
        for rec in self:
            if rec.sale_id:
                for sale in rec.sale_id.order_line:
                    if sale.product_uom_qty !=sale.qty_delivered:
                        rec.state_delivery=True
                        rec.sale_id.state_delivery='not_delivered'
                        break
                    else:
                        rec.state_delivery=True
                        rec.sale_id.state_delivery = 'delivered'







    @api.depends('so_delivery_type','sale_id','receipt_exchange_order_id')
    def check_is_exchange(self):
        self.check_exchange = False
        for rec in self:
            if rec.so_delivery_type == 'exchange' and rec.receipt_exchange_order_id:
                rec.check_exchange = True
                rec.sale_id.check_exchange_so =True
            else:
                rec.check_exchange = False
                rec.sale_id.check_exchange_so = False



    @api.depends('so_delivery_type')
    def _cumpute_is_exchange(self):
        for rec in self:
            if rec.so_delivery_type == 'exchange':
                rec.is_exchange = True
            else:
                rec.is_exchange = False
#      Nassar
#     @api.onchange('sales_order_id')
#     def _change_sales_person(self):
#         self.user_sales_id=self.sales_order_id.user_id

    # @api.depends('state','name')
    def compute_total_cocs(self):
        print("GGGGGGGGGGGGGGGGGGGGGGGGGGG")
        for res in self:
            if res.state=='done':
                total = 0.0
                print('222222222222222222222222')
                for rec in self.env['account.move'].search([]):
                    print("44444444444444444444444444444",res.name,rec.ref)
                    if str(res.name) == str(rec.ref) or str(res.name) in str(rec.ref) :
                        print("555555555555555555555555555555")
                        total+=rec.amount_total_signed
                        print("Total------------",total)

                res.total_cocs=total
                print(total,'2222222222222')
            else:
                res.total_cocs =0






    @api.onchange('location_dest_id')
    def _get_managers(self):
        _error_mesaage=''
        for rec in self:
            if rec.location_dest_id and rec.picking_type_id.code == 'internal':
                mangers = rec.location_dest_id.warehouse_id.manager_lines
                lines=[]
                for M in mangers:
                    if(M.manager_id.name):
                        _error_mesaage+=M.manager_id.name+" "
                    # print M.manager_id.name
                    line=(0,0,{
                        'warehouse_manager_id':M.manager_id,
                        'is_approved':False,
                        'has_rule':True if M.manager_id==self.env.user else False
                        })
                    lines.append(line)
                rec.approval_lines=lines




    def do_new_transfer(self):
        print (" Lol")
        """
        on validation add this id on other exchange order
        :return: super
        """
        # Load Initial Demand
        self.save_descrip_action()
        if self.receipt_exchange:
            ## in case of recipt exchange order add it's id on tendre order
            if self.delivery_exchange_order_id:
                self.delivery_exchange_order_id.write({'receipt_exchange_order_id': self.id})
        elif self.is_exchange:
            ## in case of exchange order add it's id on exhchange  order
            if self.receipt_exchange_order_id:
                self.receipt_exchange_order_id.write({'delivery_exchange_order_id': self.id})
            ## If there is no exchange order raise warning
            else:
                raise Warning("Please Set Exchange Receipt Order to be able to validate")
        ## 1- is internal transfer
        ## 2- it's location has required_approval checkbox checked
        ## 3- it's location has warehouse, and warehouse have manager
        ## 4- it's location has warehouse, and warehouse have manager and this manager didn't check approve
        pick_approved = False
        for line in self.approval_lines:
            if line.is_approved:
                pick_approved = True
                break
        # raise Warning(pick_approved )
        if self.location_dest_id.required_approval  and \
            self.location_id.required_approval  and \
            not pick_approved:
            _error_mesaage=' '
            for rec in self:
                mangers = rec.location_dest_id.warehouse_id.manager_lines
                for M in mangers:
                    if M.manager_id.name:
                        _error_mesaage+=M.manager_id.name+" OR "
            e_message=_error_mesaage[:-3]
            message ='Please ask warehouse manager ('+e_message+' ) to approve order first'
            for x in xrange(1,10):
                pass
            raise Warning(message)
        return super(StockPickingInherit, self).do_new_transfer()
## A.Salama .... Code end.


