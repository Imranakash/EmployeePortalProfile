# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import json


class SalesPortalController(http.Controller):

    @http.route(['/sales/orders'], type='http', auth='public', website=True)
    def list_orders(self, **kwargs):
        orders = request.env['sale.order'].sudo().search([], order='date_order desc')

        return request.render('sales_portal.sale_order_list_template', {
            'orders': orders,
        })


    @http.route('/sales/orders/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_order(self, **post):
        try:
            partner_id = int(post.get('partner_id'))
            product_ids = json.loads(post.get('product_ids', '[]'))
            quantities = json.loads(post.get('quantities', '[]'))

            if not partner_id:
                raise ValidationError("Customer is required")

            # Create sale order header
            order = request.env['sale.order'].sudo().create({
                'partner_id': partner_id,
                'state': 'draft',  # quotation state
                # date_order auto-fills with current datetime
            })

            # Create order lines
            for product_id, qty in zip(product_ids, quantities):
                product = request.env['product.product'].sudo().browse(product_id)

                request.env['sale.order.line'].sudo().create({
                    'order_id': order.id,
                    'product_id': product_id,
                    'product_uom_qty': float(qty),
                    'price_unit': product.list_price,  # get price from product
                })

            return request.redirect(f'/sales/orders/{order.id}')

        except Exception as e:
            return request.render('sales_portal.error_template', {
                'error': str(e)
            })

    @http.route('/sales/orders/<int:order_id>/edit', type='http', auth='public', methods=['POST'], csrf=False)
    def update_order(self, order_id, **post):
        order = request.env['sale.order'].sudo().browse(order_id)

        if not order.exists():
            return request.render('sales_portal.error_template', {
                'error': 'Order not found'
            })

        # Only allow editing draft orders
        if order.state != 'draft':
            return request.render('sales_portal.error_template', {
                'error': f'Cannot edit order in {order.state} state'
            })

        # Update allowed fields
        vals = {}

        if 'customer_reference' in post:
            vals['client_order_ref'] = post.get('customer_reference')

        if 'note' in post:
            vals['note'] = post.get('note')

        if vals:
            order.write(vals)

        return request.redirect(f'/sales/orders/{order_id}')

    @http.route('/sales/orders/<int:order_id>/delete', type='http', auth='public', methods=['POST'], csrf=False)
    def delete_order(self, order_id, **kwargs):
        order = request.env['sale.order'].sudo().browse(order_id)

        if not order.exists():
            return request.redirect('/sales/orders')

        # Only allow deleting draft orders
        if order.state != 'draft':
            return request.render('sales_portal.error_template', {
                'error': f'Cannot delete order in {order.state} state. Only draft quotations can be deleted.'
            })

        order_name = order.name
        order.unlink()  # DELETE from database

        return request.redirect('/sales/orders')
    @http.route('/sales/orders/<int:order_id>/confirm', type='http', auth='public', methods=['POST'], csrf=False)
    def confirm_order(self, order_id, **kwargs):

        order = request.env['sale.order'].sudo().browse(order_id)

        if not order.exists():
            return request.redirect('/sales/orders')

        if order.state == 'draft':
            order.action_confirm()  # Odoo built-in method
            # This changes state to 'sale' and creates delivery order

        return request.redirect(f'/sales/orders/{order_id}')
    @http.route('/sales/orders/<int:order_id>/cancel', type='http', auth='public', methods=['POST'], csrf=False)
    def cancel_order(self, order_id, **kwargs):

        order = request.env['sale.order'].sudo().browse(order_id)

        if not order.exists():
            return request.redirect('/sales/orders')

        if order.state in ['draft', 'sent', 'sale']:
            order.action_cancel()  # Odoo built-in method

        return request.redirect(f'/sales/orders/{order_id}')

    @http.route(['/my/profile'], type='http', auth='user', website=True)
    def my_profile(self, **kwargs):
        # বর্তমান লগইন করা ইউজারের সাথে যুক্ত এমপ্লয়ি রেকর্ড খুঁজে বের করা
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            # যদি ইউজারের সাথে কোনো এমপ্লয়ি কানেক্ট করা না থাকে
            return request.render('sales_portal.error_template', {
                'error': 'No employee profile linked to your user account.'
            })

        return request.render('sales_portal.user_profile_template', {
            'user': user,
            'employee': employee,
        })