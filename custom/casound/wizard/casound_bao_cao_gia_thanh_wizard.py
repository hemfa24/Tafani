from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, AccessDenied, Warning
from datetime import date
from functools import reduce
import random
import datetime
import calendar
from dateutil.relativedelta import relativedelta


def get_years_field():
    year_list = []
    for i in range(2023, 2043):
        year_list.append((i, str(i)))
    return year_list


class BaoCaoGiaThanh(models.Model):
    _name = "casound.bao_cao_gia_thanh.wizard"
    _description = "Báo cáo giá thành"
    thang = fields.Selection(
        [('01', 'Tháng 1'), ('02', 'Tháng 2'), ('03', 'Tháng 3'),
         ('04', 'Tháng 4'), ('05', 'Tháng 5'), ('06', 'Tháng 6'),
         ('07', 'Tháng 7'), ('08', 'Tháng 8'), ('09', 'Tháng 9'),
         ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')],
        string='Tháng', default=str(datetime.datetime.now().month)
    )
    nam = fields.Selection(
        [(str(r), str(r))
         for r in range(2022, datetime.datetime.now().year + 50)],
        string='Năm',
        default=str(datetime.datetime.now().year),
    )

    def get_production_orders(self, product_id):
        production_orders = self.env['mrp.production'].search(
            [('product_id', '=', product_id)])
        return production_orders

    def print_report(self):
        data = {
            'model': 'casound.bao_cao_gia_thanh.wizard',
            'form_data': self.read()[0]
        }
        thang = int(data['form_data']['thang'])
        nam = int(data['form_data']['nam'])
        hoanthanh = 'done'
        product = "product"
        chiphi = "service"
        thanhpham = 6
        chinh = 4
        phu = 5
        chiphinhancong = 7
        chiphichung = 8
        start_date = datetime.date(nam, thang, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)

        # danh sách sản phẩm và giá trị vốn
        list_thanh_pham = self.env['product.product'].search(
            [('active', '=', True) and ('detailed_type', '=', product) and ('categ_id', '=', thanhpham)])
        list_chi_phi_phan_bo = self.env['stock.landed.cost'].search(
            [('state', '=', hoanthanh) and ('date', '>=', start_date) and ('date', '<=', start_date)])

        lenhsanxuatmain = self.env['mrp.production'].search([])
        # result
        list_thanh_pham_models = []
        danhsachnhap = []
        soluongnhap = 0
        tondodang = 0
        tondodangcuoi = 0
        giatridodangdau = 0
        giatridodangcuoi = 0
        soluongnvlchinh = 0
        soluongnvlphu = 0
        chiphinhancongmain = 0
        chiphichungmain = 0
        first_day = datetime.date(nam, thang, 1)
        _, num_days = calendar.monthrange(nam, thang)
        last_day = datetime.date(nam, thang, num_days)

        tilenvlchinh = 0
        tilenvlphu = 0
        tilenhancong = 0
        tilechiphichung = 0
        totalbom = 0
        tongbom = 0  # tổng chi phí nvl
        bomchinh = 0  # chi phí nvl chính
        bomphu = 0  # chi phí nvl phụ
        giatrilenhsx = 0
        chiphinhancongfinal = 0
        chiphichungfinal = 0
        tong_chi_phi_lsx = 0
        tong_chi_phi_lsx_chua_san_pham = 0

        # tổng chi phí là 100%. trong hàm này tính ra tỉ lệ của nvl chính, phụ và tỉ lệ chi phí nhân công, chi phí chung, sau đó nhân với tổng số lượng sản phẩm sản xuất trong kỳ
        if len(list_thanh_pham) != 0:
            for i in list_thanh_pham:
                print("id", i)
                danhsachthaydoi = i['stock_quant_ids']
                lenhsanxuat = self.env['mrp.production'].search(
                    [('product_id', '=', i.id)])
                # lấy ra danh sách nguyên vật liệu của sản phẩm
                listbom = i['bom_ids'][0]['bom_line_ids']
                print(listbom)

                # tính tỉ lệ nvl chính và phụ của sản phẩm dựa trên nhóm sản phẩm
                if len(listbom) != 0:
                    for tilebom in listbom:
                        print('m', type(tilebom['product_id']['categ_id'].id))
                        tongbom += tilebom['product_id']['standard_price'] * \
                            tilebom['product_qty']
                        if tilebom['product_id']['categ_id'].id == chinh:
                            print("co bom chinh")
                            bomchinh += tilebom['product_id']['standard_price'] * \
                                tilebom['product_qty']

                        if tilebom['product_id']['categ_id'].id == phu:
                            print("co bom phu")
                            bomphu += tilebom['product_id']['standard_price'] * \
                                tilebom['product_qty']
                if tongbom > 0:
                    tylebom = tongbom / i['standard_price']
                    tilenvlchinh = bomchinh / tongbom * tylebom
                    tilenvlphu = bomphu / tongbom * tylebom
                    totalbom = tongbom
                print("bom", tilenvlchinh)
                print("bom1", tilenvlphu)
                print("bom2", totalbom)
                print(lenhsanxuat)

                # Hàm tính toán số lượng sản phẩm được sản xuất trong tháng
                if len(danhsachthaydoi) != 0:
                    for phieu in danhsachthaydoi:
                        if phieu['quantity'] > 0 and phieu['in_date'].month == thang:
                            soluongnhap += phieu['quantity']
                        # nhân công
                if len(list_chi_phi_phan_bo) != 0:
                    for phanbo in list_chi_phi_phan_bo:
                        tong_chi_phi_nc = 0
                        tong_chi_phi_chung = 0
                        tong_chi_phi_nc_cua_san_pham = 0
                        tong_chi_phi_chung_cua_san_pham = 0
                        if len(phanbo['cost_lines']) != 0:
                            for cl in phanbo['cost_lines']:
                                # tổng chi phí của lệnh sản xuất
                                if cl['product_id']['categ_id'] == chiphinhancong:
                                    tong_chi_phi_nc += cl['price_unit']  # 3
                                if cl['product_id']['categ_id'] == chiphichung:
                                    tong_chi_phi_chung += cl['price_unit']  # 4
                                # tổng giá trị của lệnh sản xuất sản phẩm
                        if len(phanbo['mrp_production_ids']) != 0:

                            for m in phanbo['mrp_production_ids']:
                                tong_chi_phi_lsx += m['product_qty'] * \
                                    m['product_id']['standard_price']  # 2
                                if m['product_id']['id'] == i.id:
                                    tong_chi_phi_lsx_chua_san_pham += m['product_qty'] * m['product_id'][
                                        'standard_price']  # 1
                        if tong_chi_phi_lsx != 0:
                            chiphinhancongfinal = (
                                tong_chi_phi_lsx_chua_san_pham / tong_chi_phi_lsx) * tong_chi_phi_nc
                            chiphichungfinal = (
                                tong_chi_phi_lsx_chua_san_pham / tong_chi_phi_lsx) * tong_chi_phi_chung

                if len(lenhsanxuat) != 0:
                    for sanxuat in lenhsanxuat:
                        print(sanxuat)
                        #     listbomlsx = sanxuat['product_id']
                        giatrilenhsx += sanxuat['product_qty'] * \
                            sanxuat['product_id']['standard_price']
                        if sanxuat['date_planned_start'].date() < first_day and (
                                sanxuat['state'] in ['confirmed', 'planned', 'progress']):
                            tondodang += sanxuat['product_qty']
                        if (sanxuat['state'] in ['confirmed', 'planned', 'progress']) and (
                                sanxuat['date_planned_start'].date() > last_day):
                            tondodangcuoi += sanxuat['product_qty']

                        # tính tỉ lệ chi phí nhân công và chi phí chung dựa trên danh sách phiếu phân bổ chi phí và nhóm sản phẩm
                        # chi phí nhân công
                        # if len(list_chi_phi_nhan_cong) != 0:
                        #     for nhancong in list_chi_phi_nhan_cong:
                        #         if len(nhancong['cost_lines']) != 0:
                        #             for cl in nhancong['cost_lines']:
                        #                 tongchiphinc += cl['price_unit']

                        #         if len(nhancong['mrp_production_ids']) != 0:
                        #             for n in nhancong['mrp_production_ids']:
                        #                 listnhancong.append(n.id)
                        #         if sanxuat.id in listnhancong:
                        #             danhsachlenhsanxuat = nhancong['mrp_production_ids']

                        #             if len(danhsachlenhsanxuat) != 0:
                        #                 for nc in danhsachlenhsanxuat:
                        #                     print(nc)
                        #                     tongchiphinhanconglsx += nc['product_qty'] * nc['product_id'][
                        #                         'standard_price']
                        #             if giatrilenhsx > 0 and tongchiphinc > 0:
                        #                 tilenhancong = tongchiphinhanconglsx / giatrilenhsx

                        #             tongchiphinhanconglsx = 0
                        #             listnhancong = []
                        #             tongchiphinc = 0

                        # chi phí chung
                        # if len(list_chi_phi_chung) != 0:
                        #     for phichung in list_chi_phi_chung:
                        #         if len(phichung['cost_lines']) != 0:
                        #             for cl in phichung['cost_lines']:
                        #                 tongchiphichung += cl['price_unit']

                        #         if len(phichung['mrp_production_ids']) != 0:
                        #             for n in phichung['mrp_production_ids']:
                        #                 listphichungid.append(n.id)
                        #         if sanxuat.id in listphichungid:
                        #             danhsachlenhsanxuat = phichung['mrp_production_ids']

                        #             if len(danhsachlenhsanxuat) != 0:
                        #                 for nc in danhsachlenhsanxuat:
                        #                     tongchiphichunglsx += nc['product_qty'] * \
                        #                                           nc['product_id']['standard_price']

                        #             if giatrilenhsx > 0 and tongchiphichung > 0:
                        #                 tilechiphichung = (
                        #                         tongchiphichunglsx / giatrilenhsx)
                        #             tongchiphichunglsx = 0
                        #             listphichungid = []
                        #             tongchiphichung = 0
                giatrungbinh = 0
                if soluongnhap != 0:
                    giatrungbinh = ((tongbom * (
                        soluongnhap + tondodang - tondodangcuoi)) + chiphichungfinal + chiphinhancongfinal) / soluongnhap

                value = {
                    "name": i['name'],
                    "masp": i['default_code'],
                    "soluongnhap": soluongnhap,
                    'giavon': giatrungbinh,
                    "giatridodangdau": tondodang * giatrungbinh,
                    "giatridodangcuoi": tondodangcuoi * giatrungbinh,
                    "tonggiathanh": soluongnhap * giatrungbinh + tondodang * giatrungbinh - tondodangcuoi * giatrungbinh,
                    'nvlchinh': bomchinh * (soluongnhap + tondodangcuoi),
                    'nvlphu': bomphu * (soluongnhap + tondodangcuoi),
                    'chiphinhancongmain': chiphinhancongfinal,
                    'chiphichungmain': chiphichungfinal,

                    'tongcong': giatrungbinh * (
                        soluongnhap + tondodangcuoi),
                    # 'chiphichungmain': (i['standard_price'] - tongbom) * (
                    #         soluongnhap + tondodangcuoi),
                    # 'chiphinhancongmain': (i['standard_price'] - tongbom) * tilenhancong * (
                    #         soluongnhap + tondodangcuoi),
                }
                list_thanh_pham_models.append(value)

                soluongnhap = 0
                tondodang = 0
                tondodangcuoi = 0
                soluongnvlchinh = 0
                soluongnvlphu = 0
                tongbom = 0  # tổng chi phí nvl
                bomchinh = 0  # chi phí nvl chính
                bomphu = 0  # chi phí nvl phụ
                totalbom = 0
                giatrilenhsx = 0
            # giá trị vốn
            # list_unit_cost = self.env['stock.valuation.layer'].search([])
            # today = date.today().strftime("%d/%m/%Y")
            todayDate = datetime.date.today()
            if todayDate.day > 25:
                todayDate += datetime.timedelta(7)

            # diadiem = data['form_data']['loction_id']

            # if len(list_san_pham) != 0:
            #     for i in list_san_pham:
            #         print(i['name'])

            data['list_san_pham'] = list_thanh_pham_models
            data['thang'] = thang
            data['nam'] = nam

            print(data)
        return self.env.ref("casound.action_bao_cao_gia_thanh_report").report_action(self, data=data)
