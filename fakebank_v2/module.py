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


from weboob.tools.backend import Module, BackendConfig
from weboob.capabilities.bank import CapBank, AccountNotFound
from weboob.tools.capabilities.bank.transactions import sorted_transactions
from weboob.tools.value import Value, ValueBool, ValueInt, ValueBackendPassword
import logging

logging.basicConfig(level=logging.INFO)
from .browser import Fakebank_v2Browser

__all__ = ['Fakebank_v2Module']


class Fakebank_v2Module(Module, CapBank):
    NAME = 'fakebank_v2'
    DESCRIPTION = 'fakebank website'
    MAINTAINER = 'Daniel'
    EMAIL = 'p_daniel@hotmail.it'
    LICENSE = 'LGPLv3+'
    VERSION = '1.5'

    BROWSER = Fakebank_v2Browser

    CONFIG = BackendConfig(Value('username', label='Username', default='foo'),  # , regexp='.+'),
                           ValueBackendPassword('password', label='Password', default='bar'),
                           )

    def iter_accounts(self):
        return self.browser.iter_accounts_list()

    def create_default_browser(self):
        return self.create_browser(self.config['username'].get(), self.config['password'].get())

        # return find_object(self.browser.get_accounts_list(), id=_id, error=AccountNotFound)


    def get_account(self, num):
        return self.browser.get_account(num)


    # def iter_coming(self, account):
    #     return self.browser.get_coming(account)

    def iter_history(self, account):
                transactions = sorted_transactions(self.browser.get_history(account))
                return transactions

        # account = find_object(self.browser.iter_accounts_list(), error=AccountNotFound, id=_id)

