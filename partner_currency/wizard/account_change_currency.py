# -*- encoding: utf-8 -*-
import logging
from odoo import models, api
from odoo.addons import decimal_precision as dp


class AccountChangeCurrency(models.TransientModel):
    _inherit = 'account.change.currency'

    @api.onchange('currency_id')
    def onchange_currency(self):
        invoice = self.get_invoice()
        if invoice.partner_id.property_purchase_currency_id:
            currency = invoice.partner_id.property_purchase_currency_id
        else:
            currency = invoice.currency_id
        if invoice.company_id.currency_id == currency:
            self.currency_rate = self.currency_id.rate
        else:
            self.currency_rate = currency.compute(1.0, self.currency_id, round=False)
        if self.currency_rate != 0.0:
            self.inverse_currency_rate = 1 / self.currency_rate
