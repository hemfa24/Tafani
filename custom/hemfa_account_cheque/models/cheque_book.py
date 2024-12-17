# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class accountJournal(models.Model):
    _inherit = "account.journal"

    cheque_book_ids = fields.One2many('cheque.book','journal_id')

class chequeBook(models.Model):
    _name = "cheque.book"

    name         =        fields.Char()
    start        =        fields.Integer()
    end          =        fields.Integer()
    journal_id   =        fields.Many2one('account.journal','Bank',domain="[('type','=','bank')]")
    note =  fields.Char()
    cheque_book_line_ids = fields.One2many('cheque.book.line','cheque_book_id')

    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
      
        default="draft",
        readonly=1,
    )
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(("Sorry you can't Delete because Record in State not in Draft"))
        
        res = super(chequeBook,self).unlink()
        return res
    def action_create_cheques(self):
        for rec in self:
            vals = []
            for x in range(rec.start,rec.end+1):
                
                vals.append({
                    'cheque_book_id':rec.id,
                    'journal_id':rec.journal_id.id,  
                    'name':x,
                    'sequance':x,
                    'page':x,
                    
                    
                })
            self.env['cheque.book.line'].create(vals)
            rec.state = 'done'
            

    def action_cancel(self):
        for rec in self:
            for line in rec.cheque_book_line_ids:
                if line.is_used:
                    raise UserError(("Sorry you can't cancel because some Chques Is Used"))
            rec.cheque_book_line_ids.unlink()
            rec.state = 'draft'
            
class chequeBookLine(models.Model):
    _name = "cheque.book.line"

    name         =        fields.Char()
    sequance     =        fields.Integer()
    page         =        fields.Integer()
    journal_id   =        fields.Many2one('account.journal','Bank',domain="[('type','=','bank')]")
    cheque_book_id = fields.Many2one('cheque.book')
    is_used = fields.Boolean('is Used?')

    account_cheque_id = fields.Many2one('account.cheque','Cheque')
    account_payment_id = fields.Many2one('account.payment','Payment')
    
    _sql_constraints = [
        ('page_journal_uniq', 'unique (journal_id,page)', 'The Index Page Of Bank Must Be unique!')
    ]

    # raise UserError(('Please Config Bank account in Jounral Configuration First'))

