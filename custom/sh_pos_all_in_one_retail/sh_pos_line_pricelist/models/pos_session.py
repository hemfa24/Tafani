# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_pricelist(self):
        if self.config_id.use_pricelist:
            domain = [('id', 'in', self.config_id.available_pricelist_ids.ids)]
        else:
            domain = [('id', '=', self.config_id.pricelist_id.id)]
        return {'search_params': {'domain': domain, 'fields': ['name', 'display_name', 'discount_policy', 'item_ids']}}


    def _pos_data_process(self, loaded_data):
        super(PosSessionInherit, self)._pos_data_process(loaded_data)
        data = loaded_data['product.pricelist']
        for pricelist in loaded_data['product.pricelist']:
            pricelist['item_ids'] = pricelist['items']
        pdata =[pp['items'] for pp in loaded_data['product.pricelist']]
        loaded_data['all_pricelists'] = data
        loaded_data['pricelist_by_id'] = {pricelist['id']: pricelist for pricelist in data}
        loaded_data['all_pricelists_item'] = pdata[0]
        loaded_data['pricelist_item_by_id'] = {pricelistItem['id']: pricelistItem for pricelistItem in pdata[0]}
        # loaded_data['all_pricelists'] = self.env['product.pricelist'].search_read()
        # loaded_data['pricelist_by_id'] = {pricelist['id']: pricelist for pricelist in self.env['product.pricelist'].search_read()}
        # loaded_data['all_pricelists_item'] = self.env['product.pricelist.item'].search_read()
        # loaded_data['pricelist_item_by_id'] = {pricelistItem['id']: pricelistItem for pricelistItem in self.env['product.pricelist.item'].search_read()}
