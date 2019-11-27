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

from urllib.parse import urlparse

import lxml
from weboob.browser.elements import ListElement, ItemElement, method, TableElement
from weboob.browser.filters.standard import CleanText, CleanDecimal, Regexp, Type, Async, Date, Env, TableCell
from weboob.browser.pages import HTMLPage, LoggedPage, pagination
from weboob.capabilities.bank import Account, Transaction
from weboob.browser.filters.html import Attr, Link
from weboob.capabilities.base import Field, NotAvailable
from weboob.core import requests
from weboob.tools.capabilities.bank.transactions import FrenchTransaction
from weboob.tools.compat import urlencode

__all__ = ['IndexPage', 'ListPage', 'LoginPage', 'HistoryPage']


class IndexPage(HTMLPage):
    pass


class ListPage(LoggedPage, HTMLPage):
    @method
    class iter_accounts(TableElement):
        head_xpath = '/html/body/table/thead'
        item_xpath = '/html/body/table/tbody/tr'

        class item(ItemElement):
            klass = Account

            obj_id = Regexp(Attr('.//a', 'href'), r'(\d+)') & Type(type=int)
            obj_label = CleanText('./td[1]')
            obj_balance = CleanDecimal('./td[2]', replace_dots=True)

            def obj_url(self):
                return (u'%s%s' % (self.page.browser.BASEURL, Link(u'.//a[1]')(self)))


class HistoryPage(LoggedPage, HTMLPage):
    @pagination
    @method
    class iter_history(TableElement):
        head_xpath = '/html/body/table/thead'
        item_xpath = '/html/body/table/tbody/tr'

        def next_page(self):
            next_page = (u'%s%s' % (self.page.browser.url.split('?', 1)[0], Link(u'//a[text()="▶"]')(self)))
            print(next_page)
            return next_page

        class item(ItemElement):
            klass = Transaction

            obj_date = Date(CleanText('./td[1]'), dayfirst=True)

            def obj_amount(self):
                return CleanDecimal('./td[3]', replace_dots=True, default=NotAvailable)(self) \
                       or CleanDecimal('./td[4]', replace_dots=True)(self)


            obj_label = CleanText('./td[2]')


class LoginPage(HTMLPage):
    def login(self, username, password):
        form = self.get_form(xpath='/html/body/fieldset/form')
        form['login'] = username
        form['password'] = password
        form.submit()
