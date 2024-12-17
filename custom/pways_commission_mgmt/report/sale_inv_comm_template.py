from odoo import api, models, _

class sale_inv_comm_template(models.AbstractModel):
    _name = 'report.pways_commission_mgmt.sale_inv_comm_template'
    _description = "Report Commission"

    @api.model
    def _get_report_values(self, docids, data=None):
        
        record_ids = self.env['sale.commission.lines'].browse(data.get('form'))
        salesperson = self.env['res.users'].browse(data.get('salesperson'))
        sales_team = self.env['crm.team'].browse(data.get('sales_team'))
        agents = self.env['res.partner'].browse(data.get('agents'))
        
        return {
               'doc_ids': self.ids,
               'doc_model': data.get('model'),
               'docs': self,
               'data' : data,
               'ids':record_ids,
               'salesperson': salesperson,
               'sales_team': sales_team,
               'agents': agents,
            }
