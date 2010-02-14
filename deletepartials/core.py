#
# core.py
#
# Copyright (C) 2009 Tom Soul <aliastomsoul@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

import os
from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

DEFAULT_PREFS = {
}

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("deletepartials.conf", DEFAULT_PREFS)
	component.get("EventManager").register_event_handler("PreTorrentRemovedEvent", self._on_pretorrent_removed)
    def disable(self):
        component.get("EventManager").deregister_event_handler("PreTorrentRemovedEvent", self._on_pretorrent_removed)
    def update(self):
        pass
    def _on_pretorrent_removed(self, torrent_id):
        files_to_remove = []
        dirs_to_remove = []
        file_priorities = component.get("TorrentManager")[torrent_id].get_status(["file_priorities"])["file_priorities"]
	files = component.get("TorrentManager")[torrent_id].get_files()
        for f, p in zip(files, file_priorities):
            if p == 0:
                files_to_remove.append(f["path"])
        save_path = component.get("TorrentManager")[torrent_id].get_status(["save_path"])["save_path"]
        for f in files_to_remove:
            if os.path.dirname(f) != '':
                 dirs_to_remove.append(os.path.dirname(f))
            filepath = os.path.join(save_path, f)
            try:
                os.remove(filepath)
            except OSError:
               pass
        for d in set(dirs_to_remove):
            dirpath = os.path.join(save_path, d)
            try:
                os.removedirs(dirpath)
            except OSError:
                pass
    @export
    def set_config(self, config):
        "sets the config dictionary"
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        "returns the config dictionary"
        return self.config.config
