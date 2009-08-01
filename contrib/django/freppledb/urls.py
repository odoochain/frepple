#
# Copyright (C) 2007 by Johan De Taeye
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA
#

# file : $URL$
# revision : $LastChangedRevision$  $LastChangedBy$
# date : $LastChangedDate$


r'''
Django URL mapping file.
'''

import os.path

from django.conf.urls.defaults import *
from django.conf import settings

import common.views
import output.urls
import input.urls
import common.urls
import admin

urlpatterns = patterns('',
    # frePPLe execution application
    (r'^execute/', include('execute.urls')),

    # Root url redirects to the admin index page
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/admin/'}),
)

# Adding urls for each installed application.
# Since the URLs don't have a common prefix (maybe they should...) we can't
# use an "include" in the previous section
urlpatterns += output.urls.urlpatterns
urlpatterns += input.urls.urlpatterns
urlpatterns += common.urls.urlpatterns

# Admin pages, and the Javascript i18n library.
# It needs to be added as the last item since the applications can
# hide/override some admin urls.
urlpatterns += patterns('',
    (r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('django.conf','freppledb'),}),
    (r'^admin/', include(admin.site.urls)),
)

# Allows the standalone development server (and the py2exe executable) to serve
# the static pages.
# In a production environment you need to configure your web server to take care of
# these pages.
if settings.STANDALONE == True:
  urlpatterns += patterns('',(r'^static/(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': os.path.join(settings.FREPPLE_APP,'static'),
        'show_indexes': False}),
    )
