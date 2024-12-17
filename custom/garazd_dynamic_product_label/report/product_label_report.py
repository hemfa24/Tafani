from odoo import models


class ReportGarazdProductLabelFromTemplate(models.AbstractModel):
    _name = 'report.garazd_dynamic_product_label.report_product_dynamic'
    _description = 'Custom Product Label Report'

    def _get_report_values(self, docids, data):
        labels = self.env['print.product.dynamic.label.line'].browse(data.get('ids', []))
        print(labels)
        return {
            'doc_model': 'print.product.dynamic.label.line',
            'doc_ids': labels.ids,
            'docs': labels,
            'data': data.get('data'),
        }
