from odoo import models, fields, api, tools, _


class libProductTmplBook(models.Model):
    _inherit = "product.template"

    is_book = fields.Boolean(strnig="Is a Book")
    book_isbn = fields.Char(string="ISBN")
    author_id = fields.Many2one('book.author', string="Authors")
    book_title = fields.Char(string="Title")
    book_genre = fields.Many2one("book.genre", string="Genre")
    book_copy_line_ids = fields.One2many("book.copies", "product_tmpl_id", string="Book Attribute")
    # book_issue_id = fields.Many2one("aht.issue.book" ,string= "book issue id") 
    issue_book_ids = fields.One2many("aht.issue.book", "book_tmpl_id", string="Book", copy=False, readonly=True,
                                     store=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(libProductTmplBook, self).create(vals_list)
        if res.is_book == True:
            res.product_variant_id.update({'is_book': True,
                                           'book_title': res.book_title if res.book_title else "",
                                           'author_id': res.author_id.id if res.author_id else False,
                                           'book_genre': res.book_genre.id if res.book_genre else False,
                                           'book_isbn': res.book_isbn if res.book_isbn else "", })

        return res


class libProductBook(models.Model):
    _inherit = "product.product"

    is_book = fields.Boolean(strnig="Is a Book")
    location_id = fields.Many2one("stock.location", string="Location")
    status = fields.Selection([
        ('Available', 'Available'),
        ('Checked out', 'Checked out')], default="Available",
        string='Status', required=True
    )

    copy_condition = fields.Selection([
        ('Unknown', 'Unknown'),
    ], default="Unknown",
        string='Condition', required=True
    )
    policy = fields.Selection([
        ('Textbook', 'Textbook'),
    ], default="Textbook",
        string='Policy', required=True
    )
    book_barcode = fields.Char('Barcode')
    serial_no = fields.Char('Serial #')


class BookAuthor(models.Model):
    _name = "book.author"

    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    name = fields.Char(string="Author name")
    author_language = fields.Char(string="Language")
    nationality = fields.Many2one("res.country", string="Nationality")

    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for template in self:
            template.can_image_1024_be_zoomed = template.image_1920 and tools.is_image_size_above(template.image_1920,
                                                                                                  template.image_1024)


class BookGenre(models.Model):
    _name = "book.genre"

    name = fields.Char(string="Genre")


class Publisher(models.Model):
    _name = "book.publisher"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Publisher name")
    country_id = fields.Many2one("res.country", string="Country of origin")


class LibBookVariant(models.Model):
    _name = "book.copies"

    location_id = fields.Many2one("stock.location", string="Location")
    status = fields.Selection([
        ('Available', 'Available'),
        ('Checked out', 'Checked out'),
        ('Lost', 'Lost')], default="Available",
        string='Status', required=True
    )
    product_tmpl_id = fields.Many2one("product.template", string="Product tmpl id")
    copy_condition = fields.Selection([
        ('Unknown', 'Unknown'),
    ], default="Unknown",
        string='Condition', required=True
    )
    policy = fields.Selection([
        ('Textbook', 'Textbook'),
    ], default="Textbook",
        string='Policy', required=True
    )
    book_barcode = fields.Char('Barcode', required=True)
    serial_no = fields.Char('Serial #')
    product_id = fields.Many2one("product.product", string="product")


class BookAwards(models.Model):
    _name = "book.awards"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Award")
    country_id = fields.Many2one('res.country', string="Country")
    can_image_1024_be_zoomed = fields.Boolean("Can Image 1024 be zoomed", compute='_compute_can_image_1024_be_zoomed',
                                              store=True)
    author_id = fields.Many2one("book.authors", string="Author")
    publisher_id = fields.Many2one("book.publisher", string="Publisher")
    book_id = fields.Many2one("product.template", string="book")

    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for template in self:
            template.can_image_1024_be_zoomed = template.image_1920 and tools.is_image_size_above(template.image_1920,
                                                                                                  template.image_1024)
