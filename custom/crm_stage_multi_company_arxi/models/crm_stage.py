from odoo import fields, models


class CrmStage(models.Model):

    _inherit = "crm.stage"

    company_ids = fields.Many2many(
        "res.company",
        string="Company",
        index=True,
        help="Specific company that uses this stage. "
        "Other companies will not be able to see or use this stage.",
        default=lambda self:
            self.env["res.company"]._company_default_get("crm.stage"),
    )
