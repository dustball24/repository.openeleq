#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#    This script is based on script.randomitems & script.watchlist
#    Thanks to their original authors

import os
import re
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import random
import urllib
import shutil
import glob, os
import time

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

__addon__     = xbmcaddon.Addon('skin.aeon.nox.silvo')
__addonid__   = __addon__.getAddonInfo('id')
__language__  = __addon__.getLocalizedString
addonPath     = xbmcaddon.Addon('skin.aeon.nox.silvo').getAddonInfo("path")
image         = os.path.join(addonPath,'notification.png')
dialog        = xbmcgui.Dialog()
cachePath     = os.path.join(xbmc.translatePath('special://home'), 'cache')
tempPath      = xbmc.translatePath('special://temp')
localtxt2     = __language__(32007)
localtxt3     = __language__(32008)
localtxt8     = __language__(32014)
localtxt9     = __language__(32028)
localtxt10    = __language__(32040)
prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass

def cache():

    localtxt1 = __language__(32006)+__language__(32000)

    destpath=xbmc.translatePath(os.path.join('special://temp',''))

    if dialog.yesno(localtxt1, localtxt3):
        shutil.rmtree(destpath)
        os.mkdir(destpath)

        xbmc.executebuiltin("Notification("+localtxt9+","+localtxt2+", 5000, %s)" % (image))

#-------------------

def packages():

    localtxt1 = __language__(32006)+__language__(32002)

    path=xbmc.translatePath(os.path.join('special://home/addons/packages',''))

    if dialog.yesno(localtxt1, localtxt3):
        shutil.rmtree(path)
        os.mkdir(path)

        xbmc.executebuiltin("Notification("+localtxt9+","+localtxt2+", 5000, %s)" % (image))

#-------------------

def musicdb():

    localtxt1 = __language__(32006)+__language__(32005)
    path = xbmc.translatePath(os.path.join('special://profile/Database',''))


    if dialog.yesno(localtxt1, localtxt3):
        database = os.path.join(path, 'MyMusic*.db')
        print database
        filelist = glob.glob(database)
        print filelist
        if filelist != []:
            for f in filelist:
                print f
                os.remove(f)
                xbmc.executebuiltin("Notification("+localtxt2+","+localtxt8+")")
                time.sleep(3)
                xbmc.executebuiltin("Reboot")
        else:
            print 'merdaa'
            xbmc.executebuiltin("Notification("+localtxt9+","+localtxt10+", 5000, %s)" % (image))

#-------------------

def videodb():

    localtxt1 = __language__(32006)+__language__(32004)
    path = xbmc.translatePath(os.path.join('special://profile/Database',''))

    if dialog.yesno(localtxt1, localtxt3):
        database = os.path.join(path, 'MyVideos*.db')
        print database
        filelist = glob.glob(database)
        print filelist
        if filelist != []:
            for f in filelist:
                print f
                os.remove(f)
                xbmc.executebuiltin("Notification("+localtxt2+","+localtxt8+")")
                time.sleep(3)
                xbmc.executebuiltin("Reboot")
        else:
            print 'merdaa'
            xbmc.executebuiltin("Notification("+localtxt9+","+localtxt10+", 5000, %s)" % (image))

#-------------------

def thumbs():

    localtxt1 = __language__(32006)+__language__(32001)

    thumbnails=xbmc.translatePath(os.path.join('special://profile/Thumbnails',''))
    path=xbmc.translatePath(os.path.join('special://profile/Database',''))

    dialog = xbmcgui.Dialog()
    if dialog.yesno(localtxt1, localtxt3):
        shutil.rmtree(thumbnails)
        os.mkdir(thumbnails)
        database = os.path.join(path, 'Textures*.db')
        print database
        filelist = glob.glob(database)
        print filelist
        if filelist != []:
            for f in filelist:
                print f
                os.remove(f)
                xbmc.executebuiltin("Notification("+localtxt2+","+localtxt8+", 5000, %s)" % (image))
                time.sleep(3)
                xbmc.executebuiltin("Reboot")
        else:
            print 'merdaa'
            xbmc.executebuiltin("Notification("+localtxt9+","+localtxt10+", 5000, %s)" % (image))

#-------------------

def advanced():

    localtxt1 = __language__(32006)+__language__(32003)


    dialog = xbmcgui.Dialog()
    if dialog.yesno(localtxt1, localtxt3):
        path = xbmc.translatePath(os.path.join('special://profile/userdata',''))
        advance=os.path.join(path, 'advancedsettings.xml')
        try:
            os.remove(advance)
            xbmc.executebuiltin("Notification(,"+localtxt2+")")
        except:
            xbmc.executebuiltin("Notification("+localtxt9+","+localtxt10+", 5000, %s)" % (image))


#-------------------


def viewsdb():

    localtxt1 = __language__(32006)+__language__(32011)
    path = xbmc.translatePath(os.path.join('special://profile/Database',''))

    if dialog.yesno(localtxt1, localtxt3):
        database = os.path.join(path, 'ViewModes*.db')
        print database
        filelist = glob.glob(database)
        print filelist
        if filelist != []:
            for f in filelist:
                print f
                os.remove(f)
                xbmc.executebuiltin("Notification("+localtxt2+","+localtxt8+", 5000, %s)" % (image))
                time.sleep(3)
                xbmc.executebuiltin("Reboot")
        else:
            print 'merdaa'
            xbmc.executebuiltin("Notification("+localtxt9+","+localtxt10+", 5000, %s)" % (image))

#-------------------

def date():

    localtxt1 = __language__(32012)
    localtxt4 = __language__(32013)
    localtxt5 = __language__(32014)

    destpath=xbmc.translatePath(os.path.join('/storage/.cache/connman',''))

    if dialog.yesno(localtxt1, localtxt3):
        shutil.rmtree(destpath)
        os.mkdir(destpath)

        xbmc.executebuiltin("Notification("+localtxt4+","+localtxt5+", 5000, %s)" % (image))
	xbmc.sleep(1000)
	xbmc.restart()

#-------------------

def deepclean():

    xbmc.executebuiltin("RunPlugin(plugin://plugin.program.openeleq.tools/?mode=update)")
    xbmc.executebuiltin("Notification(Opschonen & Verversen,Moment Geduld Alstublieft,18000,XvBMC.png)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.genesis)"):
        genesisCache = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.genesis'), 'cache.db')
        dbcon = database.connect(genesisCache)
        dbcur = dbcon.cursor()
        dbcur.execute("DROP TABLE IF EXISTS rel_list")
        dbcur.execute("VACUUM")
        dbcon.commit()
        dbcur.execute("DROP TABLE IF EXISTS rel_lib")
        dbcur.execute("VACUUM")
        dbcon.commit()
        xbmc.executebuiltin("Notification(Genesis,Cache Cleared, 5000, special://home/addons/plugin.video.genesis/icon.png)")
    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.pulsar/cmd/clear_cache)")
    xbmc.executebuiltin("RunScript(script.extendedinfo,info=deletecache)")
    if os.path.exists(cachePath)==True:
        for root, dirs, files in os.walk(cachePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    try:
                        if (f == "kodi.log" or f == "kodi.old.log"): continue
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                    except:
                        pass
            else:
                pass
    if os.path.exists(tempPath)==True:    
        for root, dirs, files in os.walk(tempPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                for f in files:
                    try:
                        if (f == "kodi.log" or f == "kodi.old.log"): continue
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                    except:
                        pass                    
            else:
                pass
    time.sleep(24)
    xbmc.executebuiltin("Notification(`Deep,Cleaned,10000,XvBMC.png)")


#-------------------

def notify(header="", message="", icon=image, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    dialog.notification(heading="Service Clean Up", message="This Addon needs arguments to run", icon=icon, time=time, sound=sound)

#-------------------


if prnum == 'cache':
    cache()

elif prnum == 'packages':
    packages()

elif prnum == 'videodb':
    videodb()

elif prnum == 'musicdb':
    musicdb()

elif prnum == 'thumbs':
    thumbs()

elif prnum == 'advanced':
    advanced()

elif prnum == 'videoviews':
    viewsdb()

elif prnum == 'date':
    date()

elif prnum == 'deepclean':
    deepclean()

elif prnum == "":
    notify()

else:
    print 'INVALID ARGUMENT'