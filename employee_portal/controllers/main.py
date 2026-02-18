from odoo import http
from odoo.http import request

class UserProfileController(http.Controller):

    @http.route(['/my/home', '/my'], type='http', auth='user', website=True)
    def my_dashboard(self, **kwargs):
        return request.render('portal.portal_my_home')

    @http.route(['/my/employees'], type='http', auth='user', website=True)
    def my_organization(self, **kwargs):
        employees = request.env['hr.employee'].sudo().search([]) # সব এমপ্লয়ি খোঁজা
        return request.render('employee_portal.portal_my_organization_template', {
            'employees': employees,
            'page_name': 'my_org',
        })

    @http.route(['/my/profile'], type='http', auth='user', website=True)
    def my_profile(self, **kwargs):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        return request.render('employee_portal.portal_my_profile_template', {
            'employee': employee,
            'page_name': 'my_profile',
        })

    @http.route(['/my/documents'], type='http', auth='user', website=True)
    def my_documents(self, **kwargs):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        return request.render('employee_portal.portal_my_documents_template', {
            'employee': employee,
            'page_name': 'my_documents',
        })