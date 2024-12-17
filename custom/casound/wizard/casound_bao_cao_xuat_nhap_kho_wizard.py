from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, AccessDenied, Warning
from datetime import date
from functools import reduce
import random
import datetime
from odoo.http import request


class BaoCaoXuatNhapKho(models.TransientModel):
    _name = "casound.bao_cao_xuat_nhap_kho.wizard"
    _description = "STOCK INVENTORY REPORT"
    ngay_ton_start = fields.Date(string="Start", required=True)

    ngay_ton_end = fields.Date(string="End", required=True)
    khohang = fields.Many2one('stock.location', string='Location', tracking=True, required=True, domain=[
        ('active', '=', True), ('usage', '=', 'view'), ('location_id', '!=', False)])

    # def get_location(self):
    #     hienthi = 'view'
    #     list_location = []
    #     list_location_main = self.env['product.product'].search(
    #         [('active', '=', True) and ('location', '!=', False) and ('usage', '=', hienthi)])
    #     keys_to_keep = ['id', 'complete_name']
    #     filtered_dict = {k: v  for k, v in list_location_main.items() if k in keys_to_keep}
    #     if len(filtered_dict):
    #         for i in filtered_dict:
    #             list_location.append(tuple(i.items()))
    #     return list_location

    def print_report(self):

        product = "product"
        user_id = request.session.uid
        user = request.env['res.users'].browse(user_id)
        # danh sách sản phẩm và giá trị vốn

        list_product_main = self.env['product.product'].search(
            [('active', '=', True) and ('detailed_type', '=', product)])

        todayDate = datetime.date.today()
        if todayDate.day > 25:
            todayDate += datetime.timedelta(7)
        data = {
            'model': 'casound.bao_cao_xuat_nhap_kho.wizard',
            'form_data': self.read()[0]
        }
        ngay_ton_start = data['form_data']['ngay_ton_start']
        ngay_ton_end = data['form_data']['ngay_ton_end']
        diadiem = self.khohang
        danhsachphieuxuat = diadiem['child_ids']['outgoing_move_line_ids']
        danhsachphieunhap = diadiem['child_ids']['incoming_move_line_ids']
        if len(danhsachphieunhap) != 0:
            for i in danhsachphieunhap:
                print(i['qty_done'])
        listkhohang = []

        list_san_pham = []

        tongtondau = 0
        tongtoncuoi = 0
        tongthaydoi = 0
        tonggiatridau = 0
        tonggiatricuoi = 0
        tonggiatrithaydoi = 0

        tongxuatdauky = 0
        tongnhapdauky = 0
        tongxuattrongky = 0
        tongnhaptrongky = 0

        tondau = 0
        toncuoi = 0
        tontrongky = 0
        if len(list_product_main) != 0:
            for i in list_product_main:
                vals = {
                    'name': i.name,
                    'masp': i.default_code,
                    'giavon': i['standard_price'],
                    'tondau': 0,
                    'toncuoi': 0,
                    'thaydoi': 0,
                    'giatridau': 0,
                    'giatricuoi': 0,
                    'giatrithaydoi': 0
                }

                if len(danhsachphieuxuat) != 0:
                    for j in danhsachphieuxuat:
                        if j['date'].date() < ngay_ton_start and j['product_id']['id'] == i.id:
                            tongxuatdauky += j['qty_done']
                        if j['date'].date() >= ngay_ton_start and j['product_id']['id'] == i.id and j[
                                'date'].date() <= ngay_ton_end:
                            tongxuattrongky += j['qty_done']
                if len(danhsachphieunhap) != 0:
                    for j in danhsachphieunhap:
                        if j['date'].date() < ngay_ton_start and j['product_id']['id'] == i.id:
                            tongnhapdauky += j['qty_done']
                        if j['date'].date() >= ngay_ton_start and j['product_id']['id'] == i.id and j[
                                'date'].date() <= ngay_ton_end:
                            tongnhaptrongky += j['qty_done']

                    tondau = tongnhapdauky - tongxuatdauky
                    tontrongky = tongnhaptrongky - tongxuattrongky
                    toncuoi = tondau + tontrongky

                    tongtondau += tondau
                    tongtoncuoi += toncuoi
                    tongthaydoi += tontrongky
                    tonggiatridau += tondau * i['standard_price']
                    tonggiatricuoi += toncuoi * i['standard_price']
                    tonggiatrithaydoi += (tonggiatricuoi - tonggiatridau)
                    vals = {
                        'name': i.name,
                        'masp': i.default_code,
                        'giavon': i['standard_price'],
                        'tondau': tondau,
                        'toncuoi': toncuoi,
                        'thaydoi': tontrongky,
                        'giatridau': tondau * i['standard_price'],
                        'giatricuoi': toncuoi * i['standard_price'],
                        'giatrithaydoi': tontrongky * i['standard_price']

                    }

                    tondau = 0
                    toncuoi = 0
                    tontrongky = 0
                    tongxuatdauky = 0
                    tongnhapdauky = 0
                    tongxuattrongky = 0
                    tongnhaptrongky = 0

                list_san_pham.append(vals)
                totaltondau = 0
                totalgiatridau = 0
                totaltoncuoi = 0
                totalgiatricuoi = 0
                totalthaydoi = 0
                totalgiatrithaydoi = 0

        if len(list_san_pham) != 0:
            for i in list_san_pham:
                totaltondau += i['tondau']
                totalgiatridau += i['giatridau']
                totaltoncuoi += i['toncuoi']
                totalgiatricuoi += i['giatricuoi']
                totalthaydoi += i['thaydoi']
                totalgiatrithaydoi += i['giatrithaydoi']

        data['list_san_pham'] = list_san_pham
        data['ngay_ton_start'] = ngay_ton_start.strftime('%d/%m/%Y')
        data['ngay_ton_end'] = ngay_ton_end.strftime('%d/%m/%Y')
        data['tongtondau'] = totaltondau
        data['tongtoncuoi'] = totaltoncuoi
        data['tongthaydoi'] = totalthaydoi
        data['tonggiatridau'] = totalgiatridau
        data['tonggiatricuoi'] = totalgiatricuoi
        data['tonggiatrithaydoi'] = totalgiatrithaydoi
        data['khohang'] = diadiem['complete_name']
        data['user_name'] = user.name
        return self.env.ref("casound.action_bao_cao_xuat_nhap_kho_report").report_action(self, data=data)
