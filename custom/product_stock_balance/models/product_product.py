# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_product(models.Model):
    """
    Overwrite to add methods to calculate locations for this product
    """
    _inherit = "product.product"

    def _compute_qty_available_total(self):
        """
        Compute method for qty_available_total

        Methods:
         * _get_sbl_qty - of product.product
        """
        self = self.with_context(total_warehouse=True)
        qtys = self._get_sbl_qty()
        for product in self:
            qty_line = qtys.get(product.id)
            product.qty_available_total = qty_line.get("qty_available")
            product.virtual_available_total = qty_line.get("virtual_available")

    qty_available_total = fields.Float(
        "Total Quantity",
        compute=_compute_qty_available_total,
        digits="Product Unit of Measure",
    )
    virtual_available_total = fields.Float(
        "Total Forecast",
        compute=_compute_qty_available_total,
        digits="Product Unit of Measure",
    )

    def action_show_table_sbl(self):
        """
        The method to open the tbale of stocks by locations
        
        Returns:
         * action of opening the table form

        Extra info:
         * Expected singleton
        """
        action_id = self.sudo().env.ref("product_stock_balance.product_product_sbl_button_only_action").read()[0]
        action_id["res_id"] = self.id
        return action_id

    def action_prepare_xlsx_balance_product(self):
        """
        To trigger the method of template
        """
        res = self.product_tmpl_id.action_prepare_xlsx_balance()
        return res

    def _get_domain_locations(self):
        """
        Overwrite core method to add check of user"s default warehouse.

        The goal is to show available quantities only for default user warehouse
        While locations table show all stocks
        """
        default_warehouse_id = self.env.user.property_warehouse_id
        if not (self._context.get("warehouse", False) or self._context.get("location", False) \
                or self._context.get("total_warehouse", False)) and default_warehouse_id:
            res = super(product_product, self.with_context(warehouse=default_warehouse_id.id))._get_domain_locations()
        else:
            res = super(product_product, self)._get_domain_locations()
        return res

    def _get_sbl_qty(self):
        """
        The method to get dict of various product qty

        Methods:
         * _compute_quantities_dict
        """
        return self._compute_quantities_dict(
            self._context.get("lot_id"), self._context.get("owner_id"), self._context.get("package_id"), 
            self._context.get("from_date"), self._context.get("to_date"),
        )
