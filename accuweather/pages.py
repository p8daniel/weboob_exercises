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

from weboob.browser.pages import HTMLPage
from dateutil.parser import parse as parse_date

from weboob.browser.elements import ItemElement, method, DictElement, ListElement
from weboob.browser.pages import JsonPage
from weboob.browser.filters.standard import Format, DateTime, Env, CleanText, Date, Regexp, CleanDecimal
from weboob.browser.filters.json import Dict
from weboob.capabilities.weather import Forecast, Current, City, Temperature
import datetime

__all__ = ['CityPage', 'WeatherPage', 'ForecastPage']


class CityPage(JsonPage):
    @method
    class iter_cities(DictElement):
        # item_xpath = '/'
        ignore_duplicate = True

        class item(ItemElement):
            klass = City

            obj_id = Dict('key')
            obj_name = Dict('localizedName')

            def obj_country(self):
                # setattr(self.obj, 'country', Dict('country')(self)['id'].lower())
                return Dict('country')(self)['id'].lower()


class WeatherPage(HTMLPage):
    def on_load(self):
        pass


    @method
    class get_current(ItemElement):
        klass = Current

        def obj_date(self):
            regex = re.compile(r'[\d]*:[\d]* [A-Z]*')
            hour = regex.findall(CleanText('//p[@class="module-header sub date"]')(self))[0].strip()
            d = datetime.datetime.strptime(hour, "%I:%M %p")

            month, day = (CleanText('/html/body/div/div[5]/div[1]/div[1]/div[3]/span'))(self).split(' ')
            the_date = datetime.datetime.now()
            # print(datetime.datetime.strptime(month, '%b'))
            the_date = the_date.replace(day=int(day), month=int(datetime.datetime.strptime(month, '%B').month),
                                        hour=d.hour, minute=d.minute, second=0, microsecond=0)

            return the_date
            # return datetime.datetime('')

        # obj_id = Env('city_id')

        def obj_temp(self):
            temp = CleanDecimal('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/div/p[1]/text()')(
                self)
            unit = CleanText(
                '/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/div/p[1]/span/text()')(self)
            return Temperature(float(temp), unit)

        # obj_text = Format('%s ', CleanText('/html/body/div/div[5]/div[1]/div/div[1]/a[1]/div/div[3]'))

        obj_text = Format('%s mbar - humidity %s%% - feels like %s°C',
                          CleanDecimal(
                              CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[4]')),
                          CleanDecimal(
                              CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[1]')),
                          CleanDecimal(
                              CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[7]')),
                          # CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[1]'),
                          # CleanText('/html/body/div/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/p[1]')
                          )

        # def obj_temp(self):

        #     temp = Dict('vt1observation/temperature')(self)
        #     return Temperature(float(temp), 'C')


class ForecastPage(HTMLPage):
    @method
    class iter_forecast(ListElement):
        item_xpath = '/html/body/div/div[5]/div[1]/div/div[1]/a'

        class item(ItemElement):
            klass = Forecast

            def obj_date(self):
                regex = re.compile(r'[\d]*/[\d]*')
                mystring = regex.findall(CleanText('./div/p[2]/text()')(self))[0].strip()
                d = datetime.datetime.strptime(mystring, '%m/%d')
                the_date = datetime.datetime.today().replace(month=d.month, day=d.day)
                return the_date.date()

            def obj_low(self):
                return Temperature(CleanDecimal('./div[2]/span[1]/text()')(self))

            def obj_high(self):
                return Temperature(CleanDecimal('./div[2]/span[2]/text()')(self))

            def obj_text(self):
                return CleanText('./span/text()')(self)

            def obj_id(self):
                return CleanText('./div/p[1]/text()')(self)
