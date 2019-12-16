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

from weboob.tools.backend import Module
from weboob.capabilities.weather import CapWeather

from .browser import AccuweatherBrowser

__all__ = ['AccuweatherModule']


class AccuweatherModule(Module, CapWeather):
    NAME = 'accuweather'
    DESCRIPTION = 'accuweather website'
    MAINTAINER = 'Daniel'
    EMAIL = 'p_daniel@hotmail.it'
    LICENSE = 'LGPLv3+'
    VERSION = '1.6'

    BROWSER = AccuweatherBrowser
    # pattern = ''

    def iter_city_search(self, pattern):
        return self.browser.iter_city_search(pattern)

    def get_current(self, city_id):

        # cities = self.iter_city_search(self.pattern)
        # for city in cities:
        #     if city.id == city_id:
        #         mycity = city
        return self.browser.get_current(city_id)

    def iter_forecast(self, city_id, test):
        print(test)
        return self.browser.iter_forecast(city_id)
