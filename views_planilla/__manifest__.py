{
    "name": "Vistas en nominas Herencia",
    "summary": "Herencia y mejoras en vistas de Nomina",
    'description': """
    """,
    'author': "@juancacorps",
    'website': "https://www.coprimex.com.gt",
    'support': "Soporte Tecnico --> soporte@gpo-r.com",
    "version": "1.0",
    "category": "Tools",
    "depends": ['hr', 'hr_payroll','base'],
    "data": [
        'views/view_nomina_individual.xml',
        'views/view_nomina.xml',
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
}
