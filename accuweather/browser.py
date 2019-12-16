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

from weboob.browser import PagesBrowser, URL
from .pages import WeatherPage, CityPage, ForecastPage


class AccuweatherBrowser(PagesBrowser):
    BASEURL = 'https://www.accuweather.com'

    # city_page = URL('https://dsx\.weather\.com/x/v2/web/loc/fr_FR/1/4/5/9/11/13/19/21/1000/1001/1003/fr%5E/\((?P<pattern>.*)\)', CityPage)
    city_page = URL('/web-api/autocomplete', CityPage)

    # city_page = URL('/fr/search-locations', CityPage)

    # weather_page = URL('/web-api/three-day-redirect', WeatherPage)
    # weather_page = URL('/web-api/three-day-redirect', WeatherPage)

    weather_page = URL(
        '/en/(?P<pattern_country>.*)/(?P<pattern_name>.*)/(?P<pattern>.*)/current-weather/(?P<pattern2>.*)',
        # '/en/(?P<pattern_country>.*)/(?P<pattern_name>.*)/(?P<pattern>.*)/weather-forecast/(?P<pattern2>.*)',
        WeatherPage)

    forecast_page = URL(
        '/en/(?P<pattern_country>.*)/(?P<pattern_name>.*)/(?P<pattern>.*)/daily-weather-forecast/(?P<pattern2>.*)',
        # '/en/(?P<pattern_country>.*)/(?P<pattern_name>.*)/(?P<pattern>.*)/weather-forecast/(?P<pattern2>.*)',
        ForecastPage)

    def iter_city_search(self, pattern):
        self.pattern = pattern
        params = {'query': pattern,
                  'language': 'en-us'}
        self.city_page.go(params=params)
        cities = self.page.iter_cities()
        return cities

    def get_current(self, city_id):
    # def get_current(self, mycity):
        params = {'key': city_id,
                  'target': ''}

        self.location('/web-api/three-day-redirect', params=params)
        # self.weather_page.go(params=params)
        # regex = re.compile(r'https://www.accuweather.com/[\w]*/[\w]*/')
        # test = regex.findall(self.url)[1].strip()
        test= self.url.split('/')

        # self.weather_page.go(pattern_country=mycity.country, pattern_name=mycity.name.lower(), pattern=mycity.id,
        #                      pattern2=mycity.id)
        self.weather_page.go(pattern_country=test[5], pattern_name=test[6], pattern=city_id,
                             pattern2=city_id)

        return self.page.get_current()

    def iter_forecast(self, mycity):
        # self.forecast_page.go(pattern_country=mycity.country, pattern_name=mycity.name.lower(), pattern=mycity.id,
        #                       pattern2=mycity.id)

        params = {'key': mycity,
                  'target': ''}
        self.location('/web-api/three-day-redirect', params=params)
        test = self.url.split('/')
        self.forecast_page.go(pattern_country=test[5], pattern_name=test[6], pattern=mycity,
                               pattern2=mycity)


        return self.page.iter_forecast()
