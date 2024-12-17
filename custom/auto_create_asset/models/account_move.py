import logging
from odoo import models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if move.move_type == 'in_invoice':
            move._create_assets()
        return move

    def _create_assets(self):
        for line in self.invoice_line_ids:
            if line.x_ctx_asset_category_id:
                ctx_category_id = line.x_ctx_asset_category_id.id
                ctx_category = self.env['ctx.account.asset.category'].browse(ctx_category_id)

                if not ctx_category.exists():
                    # Log a warning and continue
                    _logger.warning("Asset category ID %s does not exist in ctx.account.asset.category. Skipping asset creation for this line." % ctx_category_id)
                    continue

                asset_vals = {
                    'name': line.name or line.label,  # Use line label if product name is not provided
                    'category_id': ctx_category_id,  # Field for the asset category from ctx.account.asset.category
                    'value': line.price_subtotal,  # Field for the gross value
                    'date': self.invoice_date,  # Field for the date
                    'invoice_id': self.id,
                    'partner_id': self.partner_id.id,  # Correctly reference the partner_id field
                    'code': line.ref,  # Add REF field and map it to the code field on the asset
                }

                # Add account_analytic_id only if it exists
                if hasattr(line, 'account_analytic_id'):
                    asset_vals['account_analytic_id'] = line.account_analytic_id.id if line.account_analytic_id else False

                try:
                    self.env['ctx.account.asset'].create(asset_vals)
                except Exception as e:
                    raise ValidationError(_("Asset creation failed: %s") % str(e))
