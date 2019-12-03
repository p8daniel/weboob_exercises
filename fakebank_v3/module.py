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

import logging
from weboob.tools.backend import Module, BackendConfig
from weboob.capabilities.bank import CapBank
from weboob.tools.capabilities.bank.transactions import sorted_transactions
from weboob.tools.value import ValueBackendPassword, Value

from .browser import Fakebank_V3Browser
logging.basicConfig(level=logging.INFO)

__all__ = ['Fakebank_V3Module']


class Fakebank_V3Module(Module, CapBank):
    NAME = 'fakebank_v3'
    DESCRIPTION = 'fakebank_v3 website'
    MAINTAINER = 'Daniel'
    EMAIL = 'p_daniel@hotmail.it'
    LICENSE = 'LGPLv3+'
    VERSION = '1.5'

    BROWSER = Fakebank_V3Browser

    CONFIG = BackendConfig(Value('username', label='Username', default='pi'),  # , regexp='.+'),
                           ValueBackendPassword('password', label='Password', default='314159'),
                           )

    def iter_accounts(self):
        return self.browser.iter_accounts_list()

    def create_default_browser(self):
        return self.create_browser(self.config['username'].get(), self.config['password'].get())



    def get_account(self, num):
        return self.browser.get_account(num)


    def iter_history(self, account):
                transactions = sorted_transactions(self.browser.get_history(account))
                print(len(transactions))
                return transactions

