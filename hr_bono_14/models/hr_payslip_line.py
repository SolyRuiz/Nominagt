from odoo import api, fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    calculo_prestacion_anual_hr = fields.Selection([
        ('deduccion', 'Deduccion Base'),
        ('ingreso', 'Ingreso Base')
    ], "configuraciones bono 14 y aguinaldo")
