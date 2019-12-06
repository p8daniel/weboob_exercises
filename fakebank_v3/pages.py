# -*- coding: utf-8 -*-

# Copyright(C) 2019      Daniel
#
# This file is part of a weboob module.
#
# This weboob module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This weboob module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this weboob module. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import re

from six import BytesIO
from weboob.browser.elements import ListElement, ItemElement, method, DictElement
from weboob.browser.filters.html import Attr, Link
from weboob.browser.filters.json import Dict
from weboob.browser.filters.standard import CleanText, Date, Regexp, Type, CleanDecimal
from weboob.browser.pages import HTMLPage, LoggedPage, pagination

from weboob.capabilities.bank import Account, Transaction
import requests

from weboob.tools.captcha.virtkeyboard import VirtKeyboardError, MappedVirtKeyboard

__all__ = ['ListPage', 'LoginPage'  , 'HistoryPage']


class ListPage(LoggedPage, HTMLPage):
    is_here = '//div[@class="account"]'

    @method
    class iter_accounts(ListElement):
        item_xpath = '/html/body/div/div'

        class item(ItemElement):
            klass = Account

            obj_id = Regexp(Attr('./a', 'onclick'), r'(\d+)') & Type(type=int)
            obj_label = CleanText('./a/text()')
            obj_balance = CleanDecimal('.//text()', replace_dots=True)

            def obj_url(self):
                return (u'%s%s' % (self.page.browser.BASEURL, Link(u'.//a[1]')(self)))

    @pagination
    @method
    class iter_history(DictElement):
        def find_elements(self):

            item_xpath = '/html/body/script[3]'
            for el in self.el.xpath(item_xpath):

                transactions = el.text_content()
                transactions = transactions.split(';')

                for line in transactions:
                    line_cont = {}
                    line = line.split(',')
                    if len(line) != 1:
                        line_cont['label'] = line[0].strip('\nadd_transaction("')
                        line_cont['date'] = re.sub(r'"', '', line[1])
                        line_cont['amount'] = line[2].strip('")')

                        yield line_cont

        class item(ItemElement):
            klass = Transaction

            obj_amount = CleanDecimal(CleanText(Dict('amount')))
            obj_label = CleanText(Dict('label'))
            obj_date = Date(CleanText(Dict('date')))

        def next_page(self):
            if Link(u'//a[text()="▶"]')(self) is not None:
                self.page.browser.history_form['page'] = CleanDecimal(Link(u'//a[text()="▶"]'))(self)
                return requests.Request("POST", self.page.url, data=self.page.browser.history_form)


class FakebankVirtKeyboard(MappedVirtKeyboard):
    symbols = {
        '0': '512beeec87eb71b9dbb85c694e8ce980',
        '1': 'f8876ad577c3e5c6b4b96ecad8bd06ad',
        '2': '7e9d75f5a87fb71a77159acd8b0dd754',
        '3': '0dc5f23be16202f3bbd0814b5ee68691',
        '4': '87b544a64a1f4599311571e005d2ba30',
        '5': '331fb5f2eb94bc9bb81d81d9c80f59c5',
        '6': '30bfbada7bc01231097e0c1629e890ab',
        '7': '1dd1c48a32ba74b6c573a701642ceff3',
        '8': 'a44422c9bd07bea52297525ddd6906ea',
        '9': '66d3f4f96ca332511584af8a6c3f7837'
    }

    # url = "/vk.png?vkid="
    url = "https://people.lan.budget-insight.com/~ntome/fake_bank.wsgi/v3/"

    color = (255, 255, 255)

    def __init__(self, basepage):
        img_url = Attr('//img[@usemap="#vkmap"]', 'src')(basepage.doc)
        img = basepage.doc.find('//img[@usemap="#vkmap"]')

        self.url += img_url

        vkid = Attr('//input[@name="vkid"]', 'value')(basepage.doc)

        super(FakebankVirtKeyboard, self).__init__(
            BytesIO(basepage.browser.open(self.url).content),
            basepage.doc, img, self.color, convert='RGB', map_attr='href')  # , "id")
        self.check_symbols(self.symbols, basepage.browser.responses_dirname)

    def get_symbol_code(self, md5sum):
        code = MappedVirtKeyboard.get_symbol_code(self, md5sum)
        m = re.search('(\d+)', code)
        if m:
            return m.group()

    def get_string_code(self, string):
        code = ''
        for c in string:
            code += self.get_symbol_code(self.symbols[c]) + ','
        return code


class LoginPage(HTMLPage):
    def login(self, login, passwd):
        try:
            vk = FakebankVirtKeyboard(self)
        except VirtKeyboardError as err:
            print("error in virtualkeyboard")
            self.logger.exception(err)
            return False
        password = vk.get_string_code(passwd)
        form = self.get_form(xpath='/html/body/fieldset/form')
        form['login'] = login
        form['code'] = password
        print(password)
        form.submit()


class HistoryPage(LoggedPage, HTMLPage):

    def is_here(self):
        return bool(self.doc.xpath('/html/body/div/h1'))

    @pagination
    @method
    class iter_history(DictElement):
        def find_elements(self):

            item_xpath = '/html/body/script[3]'
            for el in self.el.xpath(item_xpath):

                transactions = el.text_content()
                transactions = transactions.split(';')

                for line in transactions:
                    line_cont = {}
                    line = line.split(',')
                    if len(line) != 1:
                        line_cont['label'] = line[0].strip('\nadd_transaction("')
                        line_cont['date'] = re.sub(r'"', '', line[1])
                        line_cont['amount'] = line[2].strip('")')

                        yield line_cont

        class item(ItemElement):
            klass = Transaction

            obj_amount = CleanDecimal(CleanText(Dict('amount')))
            obj_label = CleanText(Dict('label'))
            obj_date = Date(CleanText(Dict('date')))

        def next_page(self):
            if Link(u'//a[text()="▶"]')(self) is not None:
                self.page.browser.history_form['page'] = CleanDecimal(Link(u'//a[text()="▶"]'))(self)
                return requests.Request("POST", self.page.url, data=self.page.browser.history_form)
