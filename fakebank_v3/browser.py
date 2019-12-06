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

from requests.compat import basestring
from weboob.browser import PagesBrowser, URL, LoginBrowser, need_login
from weboob.capabilities.bank import AccountNotFound
from weboob.exceptions import BrowserIncorrectPassword, ActionNeeded

from .pages import LoginPage, ListPage #,HistoryPage

__all__ = ['Fakebank_V3Browser']


class Fakebank_V3Browser(LoginBrowser, PagesBrowser):
    BASEURL = 'https://people.lan.budget-insight.com/'

    login = URL('/~ntome/fake_bank.wsgi/v3/login', LoginPage)
    accounts = URL(r'https://people.lan.budget-insight.com/~ntome/fake_bank.wsgi/v3/app', ListPage)
    # account_url = URL(r'https://people.lan.budget-insight.com/~ntome/fake_bank.wsgi/v3/app', HistoryPage)

    history_form = {}


    @need_login
    def iter_accounts_list(self):

        # self.accounts.stay_or_go()
        # form = self.page.get_form()
        # form['action'] = 'accounts'
        # form.submit()

        form = {'action': 'accounts'}
        self.accounts.go(data=form)

        # self.page.get_the_page(action='accounts')
        return self.page.iter_accounts()

    def do_login(self):

        if not self.password.isdigit():
            raise BrowserIncorrectPassword()

        # Since a while the virtual keyboard accepts only the first 6 digits of the password
        self.password = self.password[:6]

        # we force the browser to go to login page so it's work even
        # if the session expire
        # Must set the referer to avoid redirection to the home page
        self.login.stay_or_go()
        # r = self.page.login(self.username, self.password)
        if not self.page.login(self.username, self.password) or self.login.is_here():
            #     # self.page.check_error()
            print("login page check errror")

    @need_login
    def get_account(self, num):
        for count, account in enumerate(self.iter_accounts_list()):
            if (count + 1) == int(num):
                return account

        raise AccountNotFound()

    @need_login
    def get_history(self, selected_account):

        self.history_form['action'] = 'history'
        self.history_form['account_id'] = selected_account.id
        self.history_form['page'] = '1'
        # self.account_url.go(data=self.history_form)
        self.accounts.go(data=self.history_form)

        for transaction in self.page.iter_history():
            yield transaction
