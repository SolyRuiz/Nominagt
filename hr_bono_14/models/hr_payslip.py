from odoo import api, fields, models

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    excluir_bono_14 = fields.Boolean('Excluir de calculo Bono 14/Aguinaldo')
    bono_14_nomina = fields.One2many('hr.bono.14', 'nomina_salida', string="Calculo Bono 14/Aguinaldo")
    total_dias_bono_14 = fields.Float()
    salario_promedio_bono_14 = fields.Float()