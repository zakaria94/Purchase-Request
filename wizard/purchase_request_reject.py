from odoo import fields, models


class PurchaseRequestReject(models.TransientModel):
    _name = 'purchase.request.reject'
    _description = 'Purchase Request Reject Reason'

    reject_reason = fields.Char(string="Rejection Reason", required=True)

    def action_confirm(self):
        purchase_request = self.env["purchase.request"].browse(self._context.get('purchase_request_id') or
                                    self._context.get('active_id'))
        print("Purchase Request ", purchase_request)
        purchase_request.rejection_reason = self.reject_reason
        

