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

import base64
import math
import random
import re

from modules.lcl.pages import myXOR
from modules.s2e.pages import S2eVirtKeyboard, BrowserIncorrectAuthenticationCode
from six import BytesIO
from weboob.browser.elements import ListElement, ItemElement, method, TableElement, DictElement
from weboob.browser.filters.html import Attr, Link
from weboob.browser.filters.json import Dict
from weboob.browser.filters.standard import CleanText, Date, Regexp, Type, CleanDecimal
from weboob.browser.pages import HTMLPage, LoggedPage, pagination, JsonPage, FormNotFound
from weboob.capabilities import NotAvailable
from weboob.capabilities.bank import Account, Transaction
from weboob.exceptions import BrowserUnavailable, BrowserQuestion, BrowserIncorrectPassword, ActionNeeded, ParseError
from weboob.tools.captcha.virtkeyboard import VirtKeyboardError, MappedVirtKeyboard, SimpleVirtualKeyboard
from weboob.tools.value import Value

__all__ = ['ListPage', 'LoginPage', 'HistoryPage']


class ListPage(LoggedPage, HTMLPage):
    def get_the_page(self, action, account_id=None, page=None):
        form = self.get_form()
        form['action'] = action
        if account_id is not None:
            form['account_id'] = account_id
        if page is not None:
            form['page'] = '1'
        form.submit()

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
    class iter_history(TableElement):
        head_xpath = '/html/body/div/table/thead'
        # item_xpath = '//*[@id="history-place"]/tr'
        item_xpath = '/html/body/div/table/thead/tbody/tr'
        print("ciao")

        class item(ItemElement):
            klass = Transaction

            obj_date = Date(CleanText('./td[1]'), dayfirst=True)
            obj_label = CleanText('./td[2]')
            obj_amount = CleanDecimal('./td[3]', replace_dots=True)

        # def next_page(self):
        #     next_page = (u'%s%s' % (self.page.browser.url.split('?', 1)[0], Link(u'//a[text()="▶"]')(self)))
        #     print(next_page)
        #     return next_page


class HistoryPage(LoggedPage, HTMLPage):
    def get_the_page(self, action, account_id=None, page=None):
        form = self.get_form()
        form['action'] = action
        if account_id is not None:
            form['account_id'] = account_id
        if page is not None:
            form['page'] = '1'
        form.submit()

    @pagination
    @method
    class iter_history(TableElement):
        head_xpath = '/html/body/div/table/thead'
        # item_xpath = '//*[@id="history-place"]/tr'
        item_xpath = '/html/body/div/table/thead/tbody/tr'
        print("ciao")

        class item(ItemElement):
            klass = Transaction

            obj_date = Date(CleanText('./td[1]'), dayfirst=True)
            obj_label = CleanText('./td[2]')
            obj_amount = CleanDecimal('./td[3]', replace_dots=True)

    # def get_my_page(self, account_id):
    #     form = self.get_form()
    #     form['action'] = 'history'
    #     form['account_id'] = account_id
    #     form['page'] = '1'
    #     form.submit()

    # @pagination
    # @method
    # class iter_history(ListElement):
    #     item_xpath = '//*[@id="history-place"]/tr'
    #
    #     class item(ItemElement):
    #         klass = Transaction
    #
    #         obj_date = Date(CleanText('./td[1]'), dayfirst=True)
    #         obj_label = CleanText('./td[2]')
    #         obj_amount = CleanDecimal('./td[3]', replace_dots=True, default=NotAvailable)


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
    url = ""

    color = (255, 255, 255)

    def __init__(self, basepage):
        img_url = Attr('//img[@usemap="#vkmap"]', 'src')(basepage.doc)
        img = basepage.doc.find('//img[@usemap="#vkmap"]')

        self.url = "https://people.lan.budget-insight.com/~ntome/fake_bank.wsgi/v3/" + img_url

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
        form.submit()
