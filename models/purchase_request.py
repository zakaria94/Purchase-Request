import odoo
from odoo import fields, models, api, _


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request Addons'

    def _get_default_user(self):
        return self.env.user

    name = fields.Char("Request Name", required=True, states={
        'approve': [('readonly', True)],
        'cancel': [('readonly', True)],
        'reject': [('readonly', True)],
    })
    user_id = fields.Many2one("res.users", default=_get_default_user, string="Request by", required=True, states={
        'approve': [('readonly', True)],
        'cancel': [('readonly', True)],
        'reject': [('readonly', True)],
    })
    start_date = fields.Date("Start Date", default=fields.Date.today(), states={
        'approve': [('readonly', True)],
        'cancel': [('readonly', True)],
        'reject': [('readonly', True)],
    })
    end_date = fields.Date("End Date", states={
        'approve': [('readonly', True)],
        'cancel': [('readonly', True)],
        'reject': [('readonly', True)],
    })
    rejection_reason = fields.Char("Rejection Reason", readonly=True,
                                   states={'draft': [('invisible', True)],
                                           'first_approve': [('invisible', True)],
                                           'approve': [('invisible', True)],
                                           'cancel': [('invisible', True)]})
    order_line_ids = fields.One2many("purchase.request.line", "purchase_request_id",
                                     states={'approve': [('readonly', True)],
                                             'cancel': [('readonly', True)],
                                             'reject': [('readonly', True)],
                                             })
    total_lines = fields.Float("Total Price", compute="_get_total_lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('first_approve', 'To Be Approved'),
        ('approve', 'Approved'),
        ('reject', 'Reject'),
        ('cancel', 'Cancel'),
    ], default='draft')

    @api.depends('order_line_ids.total_price')
    def _get_total_lines(self):
        print(self.order_line_ids.mapped('total_price'))
        self.total_lines = sum(self.order_line_ids.mapped('total_price'))

    def action_first_approve(self):
        self.write({'state': 'first_approve'})

    def action_approve(self):
        self.write({'state': 'approve'})
        users = self.env["res.users"].search([])
        purchase_manager_users = [user for user in users if user.has_group('purchase.group_purchase_manager')]
        emails = [user.login for user in purchase_manager_users if user.login]
        ctx = {}
        if emails:
            ctx['email_to'] = ','.join(emails)
            ctx['email_from'] = self.env.user.company_id.email
            ctx['send_email'] = True
            template = self.env.ref('purchase_request.send_purchase_request_approved_mail')
            template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_reject(self):
        self.write({'state': 'reject'})
        # open wizard reject reason
        return {
            'name': _('Reject Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.reject',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('purchase_request.purchase_request_reject_wizard_form').id,
            'context': {'purchase_request_id': self.id},
        }


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = "Purchase Request Lines"

    purchase_request_id = fields.Many2one("purchase.request")
    product_id = fields.Many2one("product.product", required=True)
    description = fields.Char(string="Description", related="product_id.name")
    quantity = fields.Float(string="Quantity", default=1)
    cost = fields.Float(string="Cost Price", related="product_id.standard_price")
    total_price = fields.Float("Total", compute="_get_total_line")

    @api.depends('quantity', 'cost')
    def _get_total_line(self):
        for rec in self:
            rec.total_price = rec.cost * rec.quantity
