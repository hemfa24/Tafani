# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class AssetAccountabilityTransfer(models.Model):
    _name = "asset.accountability.transfer"
    _description = "Asset Transferred"
    _inherit = ['mail.thread']


    name = fields.Char(
        string="Name",
        required=True,
        copy=False,
        default='New',
        readonly=True,
    )
    transferred_asset_id = fields.Many2one(
        'account.asset.asset.custom',
        string="Assets to be Transferred",
        required=True,
        states={'done': [('readonly', True)]}
    )
    transferred_asset_name = fields.Char(
        string="Asset Name",
        related="transferred_asset_id.name",
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self:self.env.user.company_id,
        states={'done': [('readonly', True)]},
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related="company_id.currency_id",
        states={'done': [('readonly', True)]},
        required=True
    )
    transfer_asset_category_id = fields.Many2one(
        'account.asset.category.custom',
        string="Asset Category",
        related="transferred_asset_id.category_id",
    )
    purchase_price = fields.Float(
        string="Purchase Price",
        related="transferred_asset_id.value",
        store=True,
    )
    residual_value = fields.Float(
        string="Residual Value",
        related="transferred_asset_id.value_residual",
        store=True,
    )
#    number_of_transfer = 
    source_department_id = fields.Many2one(
        'hr.department',
        string="Source Location",
        required=True,
        states={'done': [('readonly', True)]}
    )
    destination_department_id = fields.Many2one(
        'hr.department',
        string="Destination Location",
        required=True,
        states={'done': [('readonly', True)]}
    )
    source_partner_id = fields.Many2one(
        'res.partner',
        string="Source Custodian",
        required=True,
        states={'done': [('readonly', True)]}
    )
    destination_partner_id = fields.Many2one(
        'res.partner',
        string="Destination Custodian",
        required=True,
        states={'done': [('readonly', True)]}
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible Person",
        states={'done': [('readonly', True)]}
    )
    asset_transfer_type_id = fields.Many2one(
        'asset.transfer.type',
        string="Transfer Type",
        required=True,
        states={'done': [('readonly', True)]}
    )
    reson = fields.Text(
        string="Reason For Transfer",
        states={'done': [('readonly', True)]}
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
        states={'done': [('readonly', True)]}
    )
    state = fields.Selection(
        selection=[
                   ('draft','Draft'),
                   ('submitted','Submitted'),
                   ('approve','Approved'),
                   ('done','Done'),
                   ('cancelled','Cancelled'),
        ],
        string="Status",
        default='draft',
        track_visibility="onchange",
    )
    create_date = fields.Datetime(
        string="Create Date",
        default=fields.Datetime.now,
        readonly=True,
    )
    transferred_date = fields.Date(
        string="Transferred Date",
        states={'done': [('readonly', True)]}
#        default=fields.Date.today(),
    )
    received_user_id = fields.Many2one(
        'res.users',
        'Received By',
        readonly=True,
    )
    asset_sequence_number = fields.Char(
        string="Asset Sequence Number",
        related="transferred_asset_id.custom_number",
    )
    asset_description = fields.Text(
        string="Asset Discription",
        related="transferred_asset_id.custom_description"
    )
    asset_date_purchased = fields.Date(
        string="Asset Date Purchased",
        related="transferred_asset_id.custom_receive_date"
    )
    asset_purchase_cost = fields.Float(
        string="Asset Purchase Cost",
        related="transferred_asset_id.value_residual"
    )
    internal_note = fields.Text(
        string="Internal Note"
    )

    @api.onchange('transferred_asset_id')
    def onchange_transferred_asset_id(self):
        for rec in self:
            rec.source_partner_id = rec.transferred_asset_id.custom_source_partner_id.id
            rec.source_department_id = rec.transferred_asset_id.custom_source_department_id.id

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('asset.accountability.transfer') or 'New'
        vals.update({
            'name': name
            })
        return super(AssetAccountabilityTransfer, self).create(vals)

    #@api.multi
    def act_submitted(self):
        for rec in self:
            rec.state = 'submitted'

    #@api.multi
    def act_approve(self):
        for rec in self:
            rec.state = 'approve'

    #@api.multi
    def act_done(self):
        for rec in self:
            rec.state = 'done'
            rec.write({'transferred_date' : fields.Date.today(),
                       'received_user_id':self.env.uid
            })
            rec.transferred_asset_id.write({
                'custom_source_partner_id': rec.destination_partner_id.id,
                'custom_source_department_id': rec.destination_department_id.id
            })
    
    def _action_cancel(self):
        self.state = 'cancelled'
    
    #@api.multi
    def act_cancel(self):
        for rec in self:
            rec._action_cancel()
    #@api.multi
    def act_cancel_officer(self):
        for rec in self:
            rec._action_cancel()

    #@api.multi
    def act_cancel_manager(self):
        for rec in self:
            rec._action_cancel()

    #@api.multi
    def act_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    #@api.multi
    def unlink(self):
        for transfer in self:
            if transfer.state not in ['draft','cancelled']:
                raise ValidationError("Only delete in draft or cancelled state")
        return super(AssetAccountabilityTransfer, self).unlink()


class AssetTransferType(models.Model):
    _name = "asset.transfer.type"
#     _rec_name = "code"
    
    #@api.multi
    @api.depends('description', 'code')
    def name_get(self):
        res = []
        for record in self:
            description = record.description
            if record.code:
                name = '[' + record.code + '] - ' + description
            res.append((record.id, name))
        return res
    
    code = fields.Char(
        string="Code",
        required=True,
    )
    description = fields.Text(
        string="Name",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
