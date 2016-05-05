# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class account_invoice_operation_wizard(models.TransientModel):
    _name = 'account.invoice.operation.wizard'
    _description = 'Account Invoice Operation Wizard'

    @api.model
    def _get_res_id(self):
        return self._context.get('active_id', False)

    @api.model
    def _get_model(self):
        return self._context.get('active_model', False)

    plan_id = fields.Many2one(
        'account.invoice.plan',
        'Plan',
        required=True,
        ondelete='cascade',
    )
    model = fields.Char(
        default=_get_model,
        required=True,
    )
    res_id = fields.Integer(
        default=_get_res_id,
        required=True,
    )

    @api.onchange('res_id', 'model')
    def onchange_res_id(self):
        model = self.model
        res_id = self.res_id
        if res_id and model:
            if model == 'account.invoice':
                types = [self.env[model].browse(res_id).journal_id.type, False]
            # for compatibility with sale order
            elif model == 'sale.order':
                types = ['sale', False]
            else:
                raise Warning(
                    'Invoice operation with active_model %s not implemented '
                    'yet' % self.model)
            self.plan_id = self.env['account.invoice.plan'].search(
                [('type', 'in', types)],
                limit=1)
            return {'domain': {'plan_id': [
                ('type', 'in', types)]}}
        else:
            self.plan_id = False

    @api.multi
    def confirm(self):
        self.ensure_one()
        model = self.model
        res_id = self.res_id
        if not model or not res_id:
            return True
        self.plan_id.recreate_operations(
            res_id, model)
        if model == 'account.invoice' and self._context.get(
                'load_and_run', False):
            return self.env[model].browse(res_id).action_run_operations()
        return True
