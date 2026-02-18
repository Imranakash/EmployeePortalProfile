{
    'name': 'Sales Portal',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Public portal for sales orders and quotations',
    'description': """
        Sales Portal Module
        ===================
        Features:
        - Customer portal for viewing quotations and sales orders
        - Create quotation requests from website
        - Track order status (draft, sent, sale, done, cancel)
        - Product catalog browsing
        - Real-time order confirmation
    """,
    'author': 'Akash',
    'website': 'https://www.mindsynth.com',
    'depends': [
        'base',
        'sale_management',
        'website',
        'portal',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_list.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}