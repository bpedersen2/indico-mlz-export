# This file is part of Indico.
# Copyright (C) 2017 Bjoern Pedersen.
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from indico.core.plugins import WPJinjaMixinPlugin
from indico.modules.events.management.views import WPEventManagement


class WPMLZExportEventMgmt(WPJinjaMixinPlugin, WPEventManagement):
    sidemenu_option = 'mlzexport'
