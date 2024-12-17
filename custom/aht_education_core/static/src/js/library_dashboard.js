odoo.define('aht_education_core.DashboardRewrite', function (require) {
"use strict";
const ActionMenus = require('web.ActionMenus');
const ComparisonMenu = require('web.ComparisonMenu');
const ActionModel = require("web.ActionModel");
const FavoriteMenu = require('web.FavoriteMenu');
const FilterMenu = require('web.FilterMenu');
const GroupByMenu = require('web.GroupByMenu');
const Pager = require('web.Pager');
const SearchBar = require('web.SearchBar');
const { useModel } = require('web.Model');
const { Component, hooks } = owl;

var concurrency = require('web.concurrency');
var config = require('web.config');
var field_utils = require('web.field_utils');
var time = require('web.time');
var utils = require('web.utils');
var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var Dialog = require('web.Dialog');
var field_utils = require('web.field_utils');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var abstractView = require('web.AbstractView');
var _t = core._t;
var QWeb = core.qweb;



const { useRef, useSubEnv } = owl;


var LibraryDashboard = AbstractAction.extend({
    template: 'LibraryDashboardMain',
    cssLibs: [
        '/aht_education_core/static/src/css/lib/nv.d3.css'
    ],
    jsLibs: [
        '/aht_education_core/static/src/js/lib/d3.min.js'
    ],

     events: {
//             'click #btnRenew': 'UpdateRenewCount',
    },



    init: function(parent, context) {

        this._super(parent, context);
        this.dashboards_templates = ['LibraryDashboard'];

    },
   
    start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.update_cp();
                self.render_dashboards();
                self.$el.parent().addClass('oe_background_grey');
                setTimeout(function() {
                self.$('#barcode_input_field').focus();
                }, 0);
                self.$('.lookup_members').on('click', function() {
                self.fetchAndRenderPartners();
                    self.$('.members_popup').show();
                    self.$('#member_search').focus();
                });
                self.$('.lookup_books').on('click', function() {
                self.fetchAndRenderBooks();
                self.$('.book_popup').show();
                self.$('#book_search').focus();
                });
                
                 self.$('#transactions_log tbody').on('click','#btnRenew', function() {
                 
                    let row= $(this).closest('tr')[0];
                    var bookId= row.cells.item(0).innerHTML;
                    var bookRenewCount = parseInt(row.cells.item(7).innerHTML)+1;
                    row.cells.item(7).innerHTML = bookRenewCount;
                    var result = self.UpdateRenewCount(bookId);
                    console.log(result);
                    
                    var dataVal =result.then(function(resp) {
                      
                        row.cells.item(4).innerHTML =resp['due_date'];
                        console.log(resp); 
                        return resp;
                     });
                    console.log('the ultimate' + dataVal);

                });

                
                self.$('.close_book_popup').on('click', function() {
                    self.$('.book_popup').hide();
                });

                self.$('.close_members_popup').on('click', function() {
                    self.$('.members_popup').hide();
                });

                self.$('.members_table tbody').on('click', 'tr', function() {
                    var partnerId = $(this).find('.partner-id').text();
                    self.updateStudentForm(partnerId);
                    self.$('.members_popup').hide();
                });
                self.$('.book_table tbody').on('click', 'tr', function() {
                    var bookId = $(this).find('.book-id').text();
                    self.updateBookForm(bookId);
                    self.updateCopiesInfo(bookId);
                    self.$('.book_popup').hide();
                });
                self.$('#member_search').on('input', function() {
                var searchValue = $(this).val().trim();
                self.fetchAndRenderPartners2(searchValue);
            });
            self.$('#book_search').on('input', function() {
                var searchValue = $(this).val().trim();
                self.fetchAndRenderBooks2(searchValue);
            });
//                barcode
                 self.$('#barcode_input_field').on('keypress', function(event) {
                            if (event.which === 13) { // Check if Enter key is pressed
                                var barcode = $(this).val();
                                var selectedOption = self.$('#dropdown_field').val();
                                 if (barcode.toLowerCase() === 'x') {
                                self.$('.student_info').css('display', 'none');
                                self.$('.book_info').css('display', 'none');
                                var $tableBody = self.$('#transactions_log tbody');
                                $tableBody.empty();
                                }
                                else if(barcode.toLowerCase() === 'l') {
                                self.fetchAndRenderPartners();
                                self.$('.members_popup').show();
                                }
                                else if(barcode.toLowerCase() === 'b') {
                                self.fetchAndRenderPartners();
                                self.$('.book_popup').show();
                                self.fetchAndRenderBooks();
                                }
                                else {
                                    self.processBarcode(barcode, selectedOption);
                                }
//                                self.processBarcode(barcode, selectedOption);
                                // Prevent the default Enter key behavior (e.g., form submission)
                                event.preventDefault();
                            }
                        });
            });
        },
        
        
        
//         updateRenewCount: function(){
//             console.log("yeyyyyyyy")
//         },
        fetchAndRenderPartners2: function(searchValue) {
        var self = this;
        // Define the domain based on the search value
        var domain = [['is_lib_member', '=', true]];
        if (searchValue) {
            domain.push(['name', 'ilike', searchValue]);
        }

        // Fetch partners based on the domain
        rpc.query({
            model: 'res.partner',
            method: 'search_read',
            args: [domain],
            kwargs: {
                fields: ['name', 'email', 'phone'],
            },
        }).then(function(partners) {
            // Render the table with the fetched partners
            self.renderPartnerTable(partners);
        });
    },
    
    
    UpdateRenewCount:async function(record){
    
     
        var recRenew= await rpc.query({
            model: 'aht.issue.book',
            method: 'updateRenew',
            args: [{'record':parseInt(record)}],
            kwargs: {
                record: parseInt(record),
            },
          
        }).then(function(result) {
        
         return result;
        });
        return recRenew; 
        },
    
    fetchAndRenderBooks2: function(searchValue) {
        var self = this;

        var domain = [['is_book', '=', true]];
        if (searchValue) {
            domain.push(['book_title', 'ilike', searchValue]);
        }

        rpc.query({
            model: 'product.template',
            method: 'search_read',
            args: [domain],
            kwargs: {
                fields: ['book_title', 'author_id', 'book_isbn', 'image_1920'],
            },
        }).then(function(books) {
            self.renderBookTable(books);
        });
    },
        fetchAndRenderTransactionLog: async function(partnerId) {
        try {
        var int_partner_id = parseInt(partnerId);
            var transactionRecords = await rpc.query({
                model: 'aht.issue.book',
                method: 'search_read',
                 args: [[['partner_id', '=', int_partner_id]]],
                kwargs: {
                    fields: ['id', 'copy_barcode', 'book_name', 'book_issue_date','due_date','renewd_count'],
                },
            });
            if (transactionRecords){
            this.renderTransactionLog(transactionRecords);
            }

        } catch (error) {
            console.error('Error fetching transaction log:', error);
        }
    },

    renderTransactionLog: function(records) {
        var $tableBody = this.$('#transactions_log tbody');
        $tableBody.empty();

        _.each(records, function (record) {
            var $row = $('<tr>').append(
                $('<td>').addClass('aht-book-id').text(record.id).hide(),
                $('<td>').text(record.copy_barcode),
                $('<td>').text(record.book_name[1]), // Assuming book_name is a many2one field
                $('<td>').text(record.book_issue_date),
                $('<td>').text(record.due_date),
                $('<td>').text('0'),
                $('<td>').text('0'),
                $('<td>').text(record.renewd_count),
                $('<td>').innerHTML = "<button id='btnRenew'>Renew count</button>",
            );
            $tableBody.append($row);
            
            console.log(record.renewd_count)
        });
        
       

    },
        
        updateBookForm: async function(bookId) {
        try {
            var book = await this.getBookData(bookId);
            if (book) {
                this.$('.book_name').text(book.book_title);
                this.$('.book_isbn').text(book.book_isbn);
                var imageDataUrl = 'data:image/png;base64,' + book.image_1920;
                 this.$('.book_image').attr('src', imageDataUrl);
                 this.$('.book_info').css('display', 'block');

            }
        } catch (error) {
            console.error("Error updating front-end form:", error);
        }
    },
            processBarcode: async function(barcode, selectedOption) {
            if (barcode.startsWith('MB')) {
                this.searchAndUpdateMember(barcode);
            } else {
                this.searchAndUpdateBook(barcode, selectedOption);
            }
        },

        searchAndUpdateMember: async function(barcode) {
        try {
            var partnerId = await this.searchMember(barcode);
            if (partnerId) {
                this.updateStudentForm(partnerId);
            } else {
                // Handle case when member is not found
                alert('Member not found with barcode:', barcode);
            }
        } catch (error) {
            console.error('Error searching for member:', error);
        }
    },
    BookCopyDrop: async function(barcode, status) {
        try {
            var copyId = await this.searchCopyId(barcode);
            if (copyId) {
//            var copyData = await rpc.query({
//                model: 'book.copies',
//                method: 'read',
//                args: [[copyId], ['product_tmpl_id']],
//                });
//                var book_template_id = copyData[0].product_tmpl_id[0];
//                var productId = await rpc.query({
//                    model: 'product.product',
//                    method: 'search',
//                    args: [[['product_tmpl_id', '=', parseInt(book_template_id)]]],
//                });
//                var isAvailable = await this.isCopyAvailable(copyId);
//                var memberId = this.$('.student_id').text();
//                var dueDate = new Date();
//                var issue_date = new Date();
//                dueDate.setDate(dueDate.getDate() + 5);
//                var partner_id = this.$('.partner_id').text();
                var record = await rpc.query({
                    model: 'aht.issue.book',
                    method: 'search_read',
                     args: [
                    [['copy_barcode', '=', barcode], ['state', '=', 'Issued']],
                    ['partner_id'],
                    ],
                });
                if (record && record.length > 0) {
                    this.updateStudentForm(parseInt(record[0].partner_id[0]));
                }
                await rpc.query({
                    model: 'book.copies',
                    method: 'write',
                    args: [[copyId], { 'status': status }],
                });
                this.$('.book_available').text('Available')

            }
        } catch (error) {
            console.error('Error updating book copy status:', error);
        }
    },
    searchAndUpdateBook: async function(barcode, selectedOption) {
        try {
            var bookId = await this.searchBook(barcode);
            if (bookId) {
                if (selectedOption === 'checkout') {
                    await this.updateBookCopyStatus(barcode, 'Checked out');
                } else if (selectedOption === 'book_drop') {
                    await this.BookCopyDrop(barcode, 'Available');
                } else if (selectedOption === 'discard_book') {
                    console.log("discard book", barcode);
                }
                this.updateCopiesInfo(bookId);
                this.updateBookForm(bookId);
            } else {
                console.log('Book not found with barcode:', barcode);
            }
        } catch (error) {
            console.error('Error searching for book:', error);
        }
    },
        updateBookCopyStatus: async function(barcode, status) {
        try {
            var copyId = await this.searchCopyId(barcode);
            if (copyId) {
            var copyData = await rpc.query({
                model: 'book.copies',
                method: 'read',
                args: [[copyId], ['product_tmpl_id']],
                });
                var book_template_id = copyData[0].product_tmpl_id[0];
                var productId = await rpc.query({
                    model: 'product.product',
                    method: 'search',
                    args: [[['product_tmpl_id', '=', parseInt(book_template_id)]]],
                });
                var isAvailable = await this.isCopyAvailable(copyId);
                var memberId = this.$('.student_id').text();
                var dueDate = new Date();
                var issue_date = new Date();
                dueDate.setDate(dueDate.getDate() + 5);
                var partner_id = this.$('.partner_id').text();
                if (partner_id && isAvailable){
                await rpc.query({
                    model: 'aht.issue.book',
                    method: 'create',
                    args: [{
                    'book_issue_date': issue_date,
                        'book_name': parseInt(productId),
                        'partner_id': parseInt(partner_id),
                        'copy_barcode': barcode,
                        'due_date': dueDate,
                        'state': 'Issued'
                    }],
                });

                await rpc.query({
                    model: 'book.copies',
                    method: 'write',
                    args: [[copyId], { 'status': status }],
                });
                this.$('.book_available').text('Checked Out')
                this.fetchAndRenderTransactionLog(parseInt(partner_id));
                console.log('Book copy status updated successfully. Issue record created.');

                }

            }
        } catch (error) {
            console.error('Error updating book copy status:', error);
        }
    },
        isCopyAvailable: async function(copyId) {
        try {
            var availableCopies = await rpc.query({
                model: 'book.copies',
                method: 'search_count',
                args: [[['id', '=', copyId], ['status', '=', 'Available']]],
            });

            return availableCopies > 0;
        } catch (error) {
            console.error('Error checking copy availability:', error);
            return false;
        }
    },
    searchCopyId: async function(barcode) {
        try {
            var copyId = await rpc.query({
                model: 'book.copies',
                method: 'search',
                args: [[['book_barcode', '=', barcode]]],
            });
            return copyId[0] || null;
        } catch (error) {
            console.error('Error searching for book copy:', error);
            return null;
        }
    },

//    fetchCopiesData: async function(barcode) {
//        try {
//            var copiesData = await rpc.query({
//                model: 'book.copies',
//                method: 'search_read',
//                args: [[['book_barcode', '=', barcode]]],
//                kwargs: {
//                    fields: ['id', 'status'],
//                },
//            });
//
//            return copiesData || [];
//        } catch (error) {
//            console.error('Error fetching copies data:', error);
//            return [];
//        }
//    },
    updateCopiesInfo: async function(bookId) {
    try {
        var copiesData = await rpc.query({
            model: 'book.copies',
            method: 'search_read',
            args: [[['product_tmpl_id', '=', parseInt(bookId)]]],
            kwargs: {
                fields: ['id', 'status'],
            },
        });

        var totalCopies = copiesData.length;
        var availableCopies = copiesData.filter(copy => copy.status === 'Available').length;
        this.$('.copies').text(`${availableCopies} of ${totalCopies} copies available.`);
        if (availableCopies == 0){
        this.$('.book_available').text('Unavailable');
        }
    } catch (error) {
        console.error('Error updating copies info:', error);
    }
},

    searchMember: async function(barcode) {
      var result = await rpc.query({
         model: 'res.partner',
         method: 'search',
         args: [[['member_id', '=', barcode]]],
     });
     return result[0] || null;
},
        searchBook: async function(barcode) {
        var copyId = await rpc.query({
                model: 'book.copies',
                method: 'search',
                args: [[['book_barcode', '=', barcode]]],
            });
            if (copyId && copyId.length > 0) {
                var copyData = await rpc.query({
                    model: 'book.copies',
                    method: 'read',
                    args: [[copyId[0]], ['product_tmpl_id']],
                });
                if (copyData && copyData.length > 0) {
                    return copyData[0].product_tmpl_id[0] || null;
                }
            }
    },

    getBookData: async function(bookId) {
        try {
            var result = await rpc.query({
                model: 'product.template',
                method: 'read',
                args: [[parseInt(bookId)]],
                kwargs: {
                    fields: ['book_title', 'author_id', 'book_isbn', 'image_1920'],
                },
            });

            if (result.length > 0) {
                return result[0];
            }
        } catch (error) {
            console.error("Error fetching partner data:", error);
        }

        return {};
    },

        fetchAndRenderPartners: function() {
            var self = this;
            rpc.query({
                model: 'res.partner',
                method: 'search_read',
                args: [[['is_lib_member', '=', true]]],
                kwargs: {
                    fields: ['name', 'email', 'phone'],
                },
            }).then(function(partners) {
                self.renderPartnerTable(partners);
            });
        },
            fetchAndRenderBooks: function() {
            var self = this;
            rpc.query({
                model: 'product.template',
                method: 'search_read',
                args: [[['is_book', '=', true]]],
                kwargs: {
                    fields: ['book_title', 'author_id', 'book_isbn', 'image_1920'],
                },
            }).then(function(books) {
                self.renderBookTable(books);
            });
        },


        renderBookTable: function(books) {
            var $tableBody = this.$('.book_table tbody');
            $tableBody.empty();
            _.each(books, function(book) {
                var $row = $('<tr>').append(
                    $('<td>').addClass('book-id').text(book.id).hide(),
                    $('<td>').text(book.book_title),
                    $('<td>').text(book.author_id[1]),
                    $('<td>').text(book.book_isbn)
                );

                $tableBody.append($row);
            });
        },

        renderPartnerTable: function(partners) {
            var $tableBody = this.$('.members_table tbody');
            $tableBody.empty();

            _.each(partners, function(partner) {
                var $row = $('<tr>').append(
                    $('<td>').addClass('partner-id').text(partner.id).hide(),
                    $('<td>').text(partner.name),
                    $('<td>').text(partner.email),
                    $('<td>').text(partner.phone || '')
                );

                $tableBody.append($row);
            });
        },

        getPartnerData: async function(partnerId) {
        try {
            var result = await rpc.query({
                model: 'res.partner',
                method: 'read',
                args: [[parseInt(partnerId)]],
                kwargs: {
                    fields: ['id','name', 'email', 'phone', 'image_1920', 'member_id'],
                },
            });

            if (result.length > 0) {
                return result[0];
            }
        } catch (error) {
            console.error("Error fetching partner data:", error);
        }

        return {};
    },

    updateStudentForm: async function(partnerId) {
        try {
            var partner = await this.getPartnerData(partnerId);
            if (partner) {
                this.$('.name').text(partner.name);
                this.$('.student_id').text(partner.member_id);
                this.$('.partner_id').text(partner.id);
                var imageDataUrl = 'data:image/png;base64,' + partner.image_1920;
                 this.$('.student_image').attr('src', imageDataUrl);
                 this.$('.student_info').css('display', 'block');
                 this.fetchAndRenderTransactionLog(partnerId);
            }
        } catch (error) {
            console.error("Error updating front-end form:", error);
        }
    },



    render_dashboards: function() {
        var self = this;
            var templates = []
            templates = ['LibraryDashboard'];
            _.each(templates, function(template) {
                self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}));
            });
    },

    on_reverse_breadcrumb: function() {
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_hr_dashboard').empty();
            self.render_dashboards();
        });
    },

    update_cp: function() {
        var self = this;
    },


   });

    core.action_registry.add('library_dashboard', LibraryDashboard);


return LibraryDashboard;

});
