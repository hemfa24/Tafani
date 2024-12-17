# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def unlink(self):
        """
            Allow deletion of draft Treasury records only
            @this user can delete this records
        """
        if self.env.user.has_group('bi_hemfa_extend.group_payment_admin'):
            for res in self:
                if res.state != 'draft':
                    raise UserError(_(
                        """
                          Sorry, you cannot delete this record because it is confirmed.
                          Only draft records can be deleted. If you need to delete this record, 
                          you must change its status to draft first, then you will be able to delete it.
                        """
                    ))
            return super().unlink()
        else:
            raise UserError(_(
                "SORRY, you don't have permission to delete this record. Please, contact administrator!!"
            ))


class AccountCheque(models.Model):
    _inherit = "account.cheque"

    def unlink(self):
        """
            Allow deletion of draft Treasury records only
            @this user can delete this records
        """
        if self.env.user.has_group('bi_hemfa_extend.group_payment_admin'):
            for res in self:
                if res.account_cheque_type == 'outgoing':
                    if res.status != 'draft':
                        raise UserError(_(
                            """
                            Sorry, you cannot delete this record because it is confirmed.
                            Only draft records can be deleted. If you need to delete this record, 
                            you must change its status to draft first, then you will be able to delete it.
                            """
                        ))
                else:
                    if res.status1 != 'draft':
                        raise UserError(_(
                            """
                            Sorry, you cannot delete this record because it is confirmed.
                            Only draft records can be deleted. If you need to delete this record, 
                            you must change its status to draft first, then you will be able to delete it.
                            """
                        ))
            return super().unlink()
        else:
            raise UserError(_(
                "SORRY, you don't have permission to delete this record. Please, contact administrator!!"
            ))

