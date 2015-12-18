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

import urllib
import urllib2
import re
import uuid
import time
import xbmcgui
import xbmcplugin
import os
import threading
import xbmc
import xbmcaddon

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

addon         = xbmcaddon.Addon('plugin.program.openeleq.tools')
addonid       = addon.getAddonInfo('id')
language      = addon.getLocalizedString
addonPath     = xbmcaddon.Addon('plugin.program.openeleq.tools').getAddonInfo("path")
image         = os.path.join(xbmc.translatePath('special://skin'),'icon.png')
addonimage    = os.path.join(addonPath, 'icon.png')
cachePath     = os.path.join(xbmc.translatePath('special://home'), 'cache')
tempPath      = xbmc.translatePath('special://temp')
mediaPath     = os.path.join(addonPath, 'media')
dialog        = xbmcgui.Dialog()
localtxt0     = language(30000) # OpenELEQ Tools
localtxt300   = language(30300) # Delete
localtxt301   = language(30301) # ATV2
localtxt302   = language(30302) # Cache
localtxt303   = language(30303) # Temp
localtxt304   = language(30304) # Files
localtxt305   = language(30305) #  files found
localtxt306   = language(30306) # in
localtxt307   = language(30307) # 'Other'
localtxt308   = language(30308) # 'LocalAndRental'
localtxt309   = language(30309) # Do you want to delete them?
localtxt310   = language(30310) # Clearing Cache
localtxt311   = language(30311) # Reboot Required
localtxt312   = language(30312) # Rebooting
localtxt313   = language(30313) # Done


prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass

#-------------------

class cacheEntry:
    def __init__(self, namei, pathi):
        self.name = namei
        self.path = pathi

#-------------------

def setupCacheEntries():
    entries = 13 #make sure this reflects the amount of entries you have
    dialogName = ["RamFM", "MP3Streams", "4oD", "BBC iPlayer", "ITV", "Phoenix", "Youtube Music", "What The Furk", "ArtistSlideshow ArtistInfo", "ArtistSlideshow Pictures", "Music Slideshow", "Simple Downloader", "Navi-X"]
    pathName = ["special://profile/addon_data/plugin.audio.ramfm/cache", "special://profile/addon_data/plugin.audio.mp3streams/temp_dl", "special://profile/addon_data/plugin.video.4od/cache",
					"special://profile/addon_data/plugin.video.iplayer/iplayer_http_cache","special://profile/addon_data/plugin.video.itv/Images",
                    "special://profile/addon_data/plugin.video.phstreams/Cache","special://profile/addon_data/plugin.video.spotitube/cache",
                    "special://profile/addon_data/plugin.video.whatthefurk/cache","special://profile/addon_data/script.artistslideshow/ArtistInformation",
                    "special://profile/addon_data/script.artistslideshow/ArtistSlideshow","special://profile/addon_data/script.image.music.slideshow/cache",
                    "special://profile/addon_data/script.module.simple.downloader","special://profile/addon_data/script.navi-x/cache"]
    cacheEntries = []    
    for x in range(entries):
        cacheEntries.append(cacheEntry(dialogName[x],pathName[x]))    
    return cacheEntries

#-------------------

def ClearCache():
    xbmc.executebuiltin("RunPlugin(plugin://plugin.program.openeleq.tools/?mode=update)")
    if xbmc.getCondVisibility("system.hasaddon(script.icechannel)"):
        xbmc.executebuiltin("RunPlugin(plugin://script.icechannel/?indexer=tools&istream_path=%20%3a%20Tools%20%3a%20Clear%20internet%20cache...&mode=tools&name=clear_cache&notify_msg_failure=The%20operation%20failed%3b%20Please%20check%20logs.&notify_msg_header=Operation%3a%20Cache%20Cleanup&notify_msg_success=The%20operation%20completed%20successfully.)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.pulsar/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.stream)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.stream/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.kmediatorrent)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.kmediatorrent/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(script.extendedinfo)"):
        xbmc.executebuiltin("RunScript(script.extendedinfo,info=deletecache)")
    xbmc.executebuiltin("Notification("+localtxt310+", "+localtxt313+", 10000, %s)" % (image))

#-------------------

def ClearAllCache():
    xbmc.executebuiltin("RunPlugin(plugin://plugin.program.openeleq.tools/?mode=update)")
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
    if xbmc.getCondVisibility("system.hasaddon(script.icechannel)"):
        xbmc.executebuiltin("RunPlugin(plugin://script.icechannel/?indexer=tools&istream_path=%20%3a%20Tools%20%3a%20Clear%20internet%20cache...&mode=tools&name=clear_cache&notify_msg_failure=The%20operation%20failed%3b%20Please%20check%20logs.&notify_msg_header=Operation%3a%20Cache%20Cleanup&notify_msg_success=The%20operation%20completed%20successfully.)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.pulsar/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.stream)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.stream/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.kmediatorrent)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.kmediatorrent/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(script.extendedinfo)"):
        xbmc.executebuiltin("RunScript(script.extendedinfo,info=deletecache)")
    if os.path.exists(cachePath)==True:
        for root, dirs, files in os.walk(cachePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                if dialog.yesno(localtxt300 + localtxt302 + localtxt304, str(file_count) + localtxt305, localtxt309):                
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
                if dialog.yesno(localtxt300 + localtxt303 + localtxt304, str(file_count) + localtxt305, localtxt309):
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
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')        
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)        
            if file_count > 0:
                if dialog.yesno(localtxt300 + localtxt301 + localtxt302 + localtxt304, str(file_count) + localtxt305 + localtxt306 + localtxt307, localtxt309):                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))                        
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')        
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)        
            if file_count > 0:
                if dialog.yesno(localtxt300 + localtxt301 + localtxt302 + localtxt304, str(file_count) + localtxt305 + localtxt306 + localtxt308, localtxt309):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))                        
            else:
                pass
    cacheEntries = setupCacheEntries()                                         
    for entry in cacheEntries:
        clear_cache_path = xbmc.translatePath(entry.path)
        if os.path.exists(clear_cache_path)==True:    
            for root, dirs, files in os.walk(clear_cache_path):
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    if dialog.yesno("%s" %(entry.name), str(file_count) + localtxt305, localtxt309):
                        for f in files:
                            os.unlink(os.path.join(root, f))
                        for d in dirs:
                            shutil.rmtree(os.path.join(root, d))                            
                else:
                    pass
    time.sleep(10)
    xbmc.executebuiltin("Notification("+localtxt310+", "+localtxt311+", 10000, %s)" % (image))
    time.sleep(1)
    if xbmc.getCondVisibility("System.Platform.Linux") or xbmc.getCondVisibility("System.Platform.Windows"):
        xbmc.executebuiltin("RestartApp")
    else:
        xbmc.executebuiltin("Reboot")

#-------------------

def ClearSystemCache():
    xbmc.executebuiltin("RunPlugin(plugin://plugin.program.openeleq.tools/?mode=update)")
    if xbmc.getCondVisibility("system.hasaddon(script.icechannel)"):
        xbmc.executebuiltin("RunPlugin(plugin://script.icechannel/?indexer=tools&istream_path=%20%3a%20Tools%20%3a%20Clear%20internet%20cache...&mode=tools&name=clear_cache&notify_msg_failure=The%20operation%20failed%3b%20Please%20check%20logs.&notify_msg_header=Operation%3a%20Cache%20Cleanup&notify_msg_success=The%20operation%20completed%20successfully.)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.pulsar/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.stream)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.stream/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.kmediatorrent)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.kmediatorrent/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(script.extendedinfo)"):
        xbmc.executebuiltin("RunScript(script.extendedinfo,info=deletecache)")
    cacheEntries = setupCacheEntries()                                         
    if os.path.exists(cachePath)==True:
        for root, dirs, files in os.walk(cachePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                if dialog.yesno(localtxt300 + localtxt302 + localtxt304, str(file_count) + localtxt305, localtxt309):                
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
                if dialog.yesno(localtxt300 + localtxt303 + localtxt304, str(file_count) + localtxt305, localtxt309):
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
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')        
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)        
            if file_count > 0:
                if dialog.yesno(localtxt300 + localtxt301 + localtxt302 + localtxt304, str(file_count) + localtxt305 + localtxt306 + localtxt307, localtxt309):                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))                        
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')        
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)        
            if file_count > 0:
                if dialog.yesno(localtxt300 + localtxt301 + localtxt302 + localtxt304, str(file_count) + localtxt305 + localtxt306 + localtxt308, localtxt309):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))                        
            else:
                pass                
    xbmc.executebuiltin("Notification("+localtxt310+", "+localtxt313+", 10000, %s)" % (image))

#-------------------

def ClearAddonCache():
    xbmc.executebuiltin("RunPlugin(plugin://plugin.program.openeleq.tools/?mode=update)")
    if xbmc.getCondVisibility("system.hasaddon(script.icechannel)"):
        xbmc.executebuiltin("RunPlugin(plugin://script.icechannel/?indexer=tools&istream_path=%20%3a%20Tools%20%3a%20Clear%20internet%20cache...&mode=tools&name=clear_cache&notify_msg_failure=The%20operation%20failed%3b%20Please%20check%20logs.&notify_msg_header=Operation%3a%20Cache%20Cleanup&notify_msg_success=The%20operation%20completed%20successfully.)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.pulsar)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.pulsar/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.stream)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.stream/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(plugin.video.kmediatorrent)"):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.kmediatorrent/cmd/clear_cache)")
    if xbmc.getCondVisibility("system.hasaddon(script.extendedinfo)"):
        xbmc.executebuiltin("RunScript(script.extendedinfo,info=deletecache)")
    cacheEntries = setupCacheEntries()                                         
    for entry in cacheEntries:
        clear_cache_path = xbmc.translatePath(entry.path)
        if os.path.exists(clear_cache_path)==True:    
            for root, dirs, files in os.walk(clear_cache_path):
                file_count = 0
                file_count += len(files)
                if file_count > 0:
                    if dialog.yesno("%s" %(entry.name), str(file_count) + localtxt305, localtxt309):
                        for f in files:
                            os.unlink(os.path.join(root, f))
                        for d in dirs:
                            shutil.rmtree(os.path.join(root, d))                            
                else:
                    pass
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
    time.sleep(5)
    xbmc.executebuiltin("Notification("+localtxt310+", "+localtxt311+", 10000, %s)" % (image))
    time.sleep(1)
    if xbmc.getCondVisibility("System.Platform.Linux") or xbmc.getCondVisibility("System.Platform.Windows"):
        xbmc.executebuiltin("RestartApp")
    else:
        xbmc.executebuiltin("Reboot")

#-------------------

if prnum == 'clearcache':
    ClearCache()

if prnum == 'clearallcache':
    ClearAllCache()

if prnum == 'clearsystemcache':
    ClearSystemCache()

if prnum == 'clearaddoncache':
    ClearAddonCache()

else:
    print 'INVALID ARGUMENT'