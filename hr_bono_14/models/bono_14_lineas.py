from odoo import api, fields, models


class Bono14Lineas(models.Model):
    _name = "hr.bono.14.lineas"

    @api.depends('payslip_id')
    def _total_amount(self):
        for data in self:
            data.total_amount = 0
            for linea in data.payslip_id.line_ids:
                if linea.salary_rule_id.calculo_prestacion_anual_hr == 'ingreso':
                    data.total_amount += linea.total
                elif linea.salary_rule_id.calculo_prestacion_anual_hr == 'deduccion':
                    data.total_amount -= linea.total
                    
    @api.depends('payslip_id')
    def _total_deduction_bono(self):
        for data in self:
            data.total_deduction = 0
            for linea in data.payslip_id.line_ids:
                if linea.salary_rule_id.calculo_prestacion_anual_hr == 'deduccion':
                    data.total_deduction += linea.total
                else:
                	data.total_deduction += 0

    parent_id = fields.Many2one('hr.bono.14')
    total_amount = fields.Float('Total', compute="_total_amount")
    total_deduction = fields.Float('Total Prestamo Bono 14', compute="_total_deduction_bono")
    payslip_id = fields.Many2one('hr.payslip')
    total_dias = fields.Float('total_dias')


