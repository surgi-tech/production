from datetime import date
from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models
# from dateutil.relativedelta import relativedelta

# =============== Dalia Atef =============
class waiting_list_patients(models.Model):
    _name = 'waiting.list.patients'
    _order = "patient_national_id"
    _rec_name = 'patient_national_id'

    # ==================== Methods =========================


    # ==================== Fields ==========================
    patient_name = fields.Char('Patient Name', required=True)
    patient_national_id = fields.Char('National ID', required=True)
    moh_approved_operation= fields.Char('MOH Approved Operation', required=True)
    # sequence = fields.Integer('Sequence', default=0)
    is_active = fields.Boolean('Active', default=True)
