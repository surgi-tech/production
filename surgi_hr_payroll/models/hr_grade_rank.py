from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import tools, _
import time
import babel
import logging

class GradeGrade(models.Model):
    _name = 'grade.grade'

    name = fields.Char('Name')
    description = fields.Text('Description')
    rank_ids = fields.One2many('rank.rank', 'grade_id', 'Ranks')
    car_allow = fields.Float('Car Allowance', track_visibility='onchange', digits=dp.get_precision('Payroll'))
    travel_expenses_allow = fields.Float('Travel Exp Allow.', track_visibility='onchange',
                                         digits=dp.get_precision('Payroll'))
    travel_allow_int_f = fields.Float('Travel Allow internal Fixed', track_visibility='onchange',
                                      digits=dp.get_precision('Payroll'))

class RankRank(models.Model):
    _name = 'rank.rank'

    name = fields.Char('Name')
    description = fields.Text('Description')
    salary_range = fields.Text('Salary Range')
    # total_salary = fields.Float('Salary',track_visibility='onchange',digits=dp.get_precision('Payroll'))
    grade_id = fields.Many2one('grade.grade', 'Grade')
    #     rang_ids = fields.Many2one('rang.rang', 'Rang')
    rang_ids = fields.One2many('rang.rang', 'rank_id', 'Rangs')



class RangRang(models.Model):
    _name = 'rang.rang'

    name = fields.Char('Name')
    description = fields.Text('Description')
    total_salary = fields.Float('Salary',track_visibility='onchange',digits=dp.get_precision('Payroll'))
    # car_allow = fields.Float('Car Allowance',track_visibility='onchange',digits=dp.get_precision('Payroll'))
    # travel_expenses_allow = fields.Float('Travel Exp Allow.',track_visibility='onchange',digits=dp.get_precision('Payroll'))
    # travel_allow_int_f = fields.Float('Travel Allow internal Fixed',track_visibility='onchange',digits=dp.get_precision('Payroll'))
    rank_id = fields.Many2one('rank.rank', 'Rank')

class HrEmployee(models.Model):

    _inherit = 'hr.contract'

    grade_id = fields.Many2one('grade.grade', 'Grade')
    rank_id = fields.Many2one('rank.rank', 'Rank')
    rang_id = fields.Many2one('rang.rang', 'Rang')
    grade_total_salary = fields.Float('Grade Salary',  related='rang_id.total_salary', readonly=True)

    @api.onchange('grade_id')
    def onchange_grade(self):
        res = {}
        if self.grade_id:
            self.rank_id = False
            res['domain'] = \
                {'rank_id': [
                    ('id', 'in', self.grade_id.rank_ids.ids)]}
        return res

    @api.onchange('rank_id')
    def onchange_rank(self):
        res = {}
        if self.rank_id:
            self.rang_id = False
            res['domain'] = \
                {'rang_id': [
                    ('id', 'in', self.rank_id.rang_ids.ids)]}
        return res



class HrEmployee(models.Model):

    _inherit = 'hr.employee'
    department_id=fields.Many2one('hr.department',related='contract_id.department_id',store=True)
    job_id=fields.Many2one('hr.job', related='contract_id.job_id',store=True)
    grade_id = fields.Many2one('grade.grade', related='contract_id.grade_id', readonly=True)
    rank_id = fields.Many2one('rank.rank',  related='contract_id.rank_id', readonly=True)
    rang_id = fields.Many2one('rang.rang',  related='contract_id.rang_id', readonly=True)



class HRDeprat(models.Model):
    _inherit = 'hr.department'











    # @api.onchange('grade_id')
    # def onchange_grade(self):
    #     res = {}
    #     if self.grade_id:
    #         self.rank_id = False
    #         res['domain'] = \
    #             {'rank_id': [
    #                 ('id', 'in', self.grade_id.rank_ids.ids)]}
    #     return res
    #
    # @api.onchange('rank_id')
    # def onchange_rank(self):
    #     res = {}
    #     if self.rank_id:
    #         self.rang_id = False
    #         res['domain'] = \
    #             {'rang_id': [
    #                 ('id', 'in', self.rank_id.rang_ids.ids)]}
    #     return res
