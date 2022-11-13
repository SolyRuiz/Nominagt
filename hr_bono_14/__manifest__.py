{
    "name": "Hr bono 14/Aguinaldo",
    "summary": "HR bono 14/Aguinaldo",
    'description': """
    """,
    'author': "Xetechs, S.A. and COPRIMEX",
    'website': "https://www.xetechs.com",
    'support': "Juan Carlos R. Ortega --> juancacorps",
    "version": "1.0",
    "category": "Tools",
    "depends": ['hr', 'hr_payroll'],
    "data": [
        'views/hr_bono_14.xml',
        'views/hr_payslip.xml',
        'views/menu.xml',
        'security/acces_rules.xml',
        'security/ir.model.access.csv',
        'views/hr_salary_rule.xml'
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
}