from odoo import api, fields, models

# BONO 14 Y AGUINALDO
class Bono14(models.Model):
    _name = "hr.bono.14"

    contract_id = fields.Many2one('hr.contract', string="Contrato", required=True)
    calculate_hr = fields.Selection([('aguinaldo', 'Aguinaldo'),('bono14', 'Bono 14'),],'Tipo de Calculo', default='aguinaldo')
    type_contract = fields.Selection([('complet', 'Año Completo'),('incomplet', 'Año Incompleto'),],'Tipo de Contrato', default='complet')
    month_division_mean_year_incomplete = fields.Float('División Meses Laborados', default=1.0)
    salary_mean_year_incomplete = fields.Float('Salario Promedio', compute='_salary_mean_year_incomplete')
    salary_not_deduction = fields.Float('Salario sin deduccion', compute='_salary_not_deduction')
    deduction_bono = fields.Float('Prestamos Bono 14', readonly=True)
    inicio = fields.Date("Inicio periodo", required=True)
    fin = fields.Date("Fin de periodo", required=True)
    final_amount = fields.Float("Total calculado", compute="_division_de_periodods")
    nomina_salida = fields.Many2one('hr.payslip', "Nomina de salida")
    lineas_ids = fields.One2many('hr.bono.14.lineas','parent_id',"Lineas de salario", readonly=True)
    division_de_periodods = fields.Integer('Cantidad de periodos para dividir', default=12)
    company_id = fields.Many2one('res.company', related='contract_id.company_id', string="Compañia")
    salario_dia = fields.Float('Salario por dia')
    total_salario_por_dia = fields.Float('Bono calculado por dias trabajados', readonly=True, compute="_total_por_dias")
    total_dias  = fields.Float(compute="_total_por_dias")


    def action_set_lineas_ids(self):
        for data in self:
            salarios = self.env['hr.payslip'].search([
                ('date_from', '>=', data.inicio),
                ('date_to', '<=', data.fin),
                ('contract_id', '=', data.contract_id.id),
                ('state','=','done'),
                ('excluir_bono_14', '=', False)
            ])
            data.create_lineas_ids(salarios)

    def create_lineas_ids(self, payslips):
        self.clean_lineas_ids()
        for payslip in payslips:
            total_dias = 0
            for dias in payslip.worked_days_line_ids:
                if dias.name.lower() == 'asistencia':
                    total_dias += dias.number_of_days

            self.env['hr.bono.14.lineas'].create({
                'parent_id': self.id,
                'payslip_id': payslip.id,
                'total_dias': total_dias
            })

    def clean_lineas_ids(self):
        for data in self:
            data.lineas_ids = [(5, 0, 0)]
            
    @api.depends('deduction_bono','final_amount')        
    def _salary_not_deduction(self):
        # Cuando el empleado tiene un adelanto de BONO 14, se le tiene que
        # Realizar una dedución de bono 14: 
        for data in self:
            if not data.deduction_bono:
                data.salary_not_deduction = 0
            if not data.final_amount:
                data.final_amount = 0
            data.salary_not_deduction = data.deduction_bono + data.final_amount

    @api.depends('calculate_hr','division_de_periodods','lineas_ids','type_contract','salary_mean_year_incomplete','total_dias')
    def _division_de_periodods(self):
        # Calculo PRINCIPAL (final_amount) a recibir en prestaciones BONO 14 o AGUINALDO
        for data in self:
            if data.calculate_hr == 'bono14': # Calculo de Bono 14
                if data.type_contract == 'complet':
                    # Final Amount (SALARIO A DEVENGAR BONO 14) si el año es completo
                    if data.lineas_ids:
                        data.deduction_bono = sum(data.lineas_ids.mapped('total_deduction'))
                        data.final_amount = sum(data.lineas_ids.mapped('total_amount'))/12
                    else:
                        data.deduction_bono = 0
                        data.final_amount =  0
                else: 
                    for data in self:
                    # Final Amount (SALARIO A DEVENGAR BONO 14) si el año es incompleto
                        if data.salary_mean_year_incomplete and data.lineas_ids:
                            data.deduction_bono = sum(data.lineas_ids.mapped('total_deduction'))
                            data.final_amount = (data.salary_mean_year_incomplete * data.total_dias) / 365
                        else:
                            data.final_amount = 0
                            data.deduction_bono = 0
            else: 
                # Calculo de Aguinaldo 
                # Condicionando si el año es completo o incompleto.

                # Salario Promedio año completo (Aguinaldo)
                if data.type_contract == 'complet':
                    # Aguinaldo Neto: Salario Promedio/360*Días laborados
                    try:
                        salary_mean_aguinaldo_local = sum(data.lineas_ids.mapped('total_amount'))/12
                        days_works = data.total_dias or 0
                        data.final_amount = (salary_mean_aguinaldo_local/360)*days_works
                    except:
                        pass
                # Salario Promedio año incompleto (Aguinaldo)     
                else: 
                    # Aguinaldo Neto: Salario Promedio/360*Días laborados
                    try: 
                        moths_incomplete = data.month_division_mean_year_incomplete or 0
                        salary_mean_aguinaldo_local = sum(data.lineas_ids.mapped('total_amount'))/moths_incomplete
                        days_works = data.total_dias or 0
                        data.final_amount = (salary_mean_aguinaldo_local/360)*days_works
                    except:
                        pass




    @api.depends('month_division_mean_year_incomplete','lineas_ids')
    def _salary_mean_year_incomplete(self):
        # Salario Promedio cuando esta activo año incompleto (BONO 14)
        # Calculo necesario para la funcion _division_de_periodods
        for data in self:
            if data.month_division_mean_year_incomplete:
                data.salary_mean_year_incomplete = sum(data.lineas_ids.mapped('total_amount'))/data.month_division_mean_year_incomplete
            else:
                data.salary_mean_year_incomplete = 0

    @api.depends('lineas_ids','type_contract','calculate_hr')
    def action_set_new_payslip_entry(self):
        # Funcion para enviar el calculo a la planilla a pagar de la planilla
        # Buscando el codigo de la regla salarial que corresponde
        if self.calculate_hr == 'aguinaldo':
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'AGUINALDO')])
        else:
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'BONO14CA')])
        if self.nomina_salida and input_type:
            self.env['hr.payslip.input'].create({
                'input_type_id': input_type[0].id,
                'amount': self.final_amount,
                'payslip_id': self.nomina_salida.id,
                'contract_id': self.contract_id})
        for data in self:
            # informacion enviada a hr_payslip.py (NOMINA DE SALIDA) REPORTE DE NOMINA
            if data.calculate_hr == 'bono14': # Bono 14
                if data.type_contract == 'incomplet':
                    amount_total_local = sum(data.lineas_ids.mapped('total_amount'))
                    data.nomina_salida.salario_promedio_bono_14 = round(amount_total_local/data.month_division_mean_year_incomplete,2)
                else:
                    amount_total_local = sum(data.lineas_ids.mapped('total_amount'))
                    data.nomina_salida.salario_promedio_bono_14 = round(amount_total_local/12,2)
            else: # Aguinaldo
                if data.type_contract == 'incomplet':
                    salary_mean_aguinaldo_local = sum(data.lineas_ids.mapped('total_amount'))/data.total_dias   
                    data.nomina_salida.salario_promedio_bono_14 = round(salary_mean_aguinaldo_local,2)
                else:
                    salary_mean_aguinaldo_local = (data.contract_id.wage * 12)/12
                    data.nomina_salida.salario_promedio_bono_14 = round(salary_mean_aguinaldo_local,2)
            # Dias laborados del trabajador
            data.nomina_salida.total_dias_bono_14 = round(data.total_dias,2)



    @api.onchange('contract_id')
    def _onchange_producer_id(self):
        for data in self:
            return {'domain': {'nomina_salida': [('contract_id', '=', data.contract_id.id)]}}
    
    @api.onchange('salario_dia')
    def _total_por_dias(self):
        # Total dias trabajados
        for data in self:
            total_dias = sum(data.lineas_ids.mapped('total_dias')) or 0
            data.total_salario_por_dia = ( total_dias * data.salario_dia)/12
            data.total_dias = total_dias

