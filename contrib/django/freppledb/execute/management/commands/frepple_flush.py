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
# Foundation Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

# file : $URL$
# revision : $LastChangedRevision$  $LastChangedBy$
# date : $LastChangedDate$

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.conf import settings
from django.utils.translation import ugettext as _

from execute.models import log
from input.models import Plan


class Command(BaseCommand):
  help = '''
  This command empties the contents of all data tables in the frePPLe database.

  The results are similar to the 'flush input output' command, with the
  difference that some tables are not emptied and some performance related
  tweaks.
  Another difference is that the initial_data fixture is not loaded.
  '''
  option_list = BaseCommand.option_list + (
      make_option('--user', dest='user', type='string',
        help='User running the command'),
      make_option('--nonfatal', action="store_true", dest='nonfatal', 
        default=False, help='Dont abort the execution upon an error'),
      )

  requires_model_validation = False

  def get_version(self):
    return settings.FREPPLE_VERSION

  @transaction.commit_manually
  def handle(self, **options):
    # Make sure the debug flag is not set!
    # When it is set, the django database wrapper collects a list of all sql
    # statements executed and their timings. This consumes plenty of memory
    # and cpu time.
    tmp_debug = settings.DEBUG
    settings.DEBUG = False

    # Pick up options
    if 'user' in options: user = options['user'] or ''
    else: user = ''
    nonfatal = False
    if 'nonfatal' in options: nonfatal = options['nonfatal']

    try:
      # Logging message
      log(category='ERASE', theuser=user,
        message=_('Start erasing the database')).save()
      cursor = connection.cursor()

      # Delete all records from the tables
      sql_list = connection.ops.sql_flush(no_style(), [
        'out_problem','out_flowplan','out_loadplan','out_demandpegging',
        'out_operationplan','demand','forecastdemand','forecast','flow',
        'resourceload','buffer','resource','setuprule','setupmatrix',
        'operationplan','item','suboperation','operation','location',
        'bucket','calendar','customer'
        ], [] )
      for sql in sql_list:
        cursor.execute(sql)
        transaction.commit()

      # SQLite specials
      if settings.DATABASE_ENGINE == 'sqlite3':
        cursor.execute('vacuum')   # Shrink the database file

      # Mark the last-modified field of the plan. This is used to force
      # browser clients to refresh any cached reports.
      Plan.objects.all()[0].save()

      # Logging message
      log(category='ERASE', theuser=user,
        message=_('Finished erasing the database')).save()
        
    except Exception, e:
      try: log(category='RUN', theuser=user,
        message=u'%s: %s' % (_('Failed erasing the database'),e)).save()
      except: pass
      if nonfatal: raise e
      else: raise CommandError(e)
      
    finally:
      transaction.commit()
      settings.DEBUG = tmp_debug
