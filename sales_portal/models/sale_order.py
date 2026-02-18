# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order - Portal Extension'

    portal_visible = fields.Boolean(
        string='Visible on Portal',
        default=True,
        help='If unchecked, this order will not appear in the public portal.'
    )

    customer_note = fields.Text(
        string='Customer Note',
        help='Notes added by the customer from the portal.'
    )

    portal_access_token = fields.Char(
        string='Portal Access Token',
        copy=False,
        help='Security token for public access without login.'
    )

    # Computed field: days since order
    days_since_order = fields.Integer(
        string='Days Since Order',
        compute='_compute_days_since_order',
        store=False,
    )

    @api.depends('date_order')
    def _compute_days_since_order(self):

        from datetime import datetime
        today = fields.Date.today()

        for order in self:
            if order.date_order:
                order_date = order.date_order.date()
                delta = today - order_date
                order.days_since_order = delta.days
            else:
                order.days_since_order = 0

    @api.model_create_multi
    def create(self, vals_list):
        import secrets

        for vals in vals_list:
            # Generate secure random token for public access
            if not vals.get('portal_access_token'):
                vals['portal_access_token'] = secrets.token_urlsafe(32)

        # Call parent create (actual database INSERT)
        orders = super(SaleOrder, self).create(vals_list)

        return orders

    def get_portal_url(self):

        self.ensure_one()  # only works on single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/sales/orders/{self.id}?access_token={self.portal_access_token}"

    def can_be_deleted(self):
        self.ensure_one()
        return self.state == 'draft'

    def can_be_edited(self):
        self.ensure_one()
        return self.state == 'draft'

    def unlink(self):
        for order in self:
            if order.state not in ['draft', 'cancel']:
                raise ValidationError(
                    f"Cannot delete order {order.name} in state '{order.state}'. "
                    f"Only draft or cancelled orders can be deleted."
                )

        # Call parent unlink (actual database DELETE)
        return super(SaleOrder, self).unlink()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line - Portal Extension'

    # Custom field: customer can add notes to individual lines
    line_note = fields.Char(
        string='Line Note',
        help='Customer note for this specific product line.'
    )

    @api.constrains('product_uom_qty')
    def _check_quantity_positive(self):
        for line in self:
            if line.product_uom_qty <= 0:
                raise ValidationError(
                    f"Quantity must be greater than 0. "
                    f"Current: {line.product_uom_qty}"
                )