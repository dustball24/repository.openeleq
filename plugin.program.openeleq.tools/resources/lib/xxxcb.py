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
password      = addon.getSetting('xxx_password')
localtxt0     = language(30000) # OpenELEQ Tools
localtxt004   = language(30004) # XXX
localtxt013   = language(30013) # Password
localtxt314   = language(30314) # XXX
localtxt315   = language(30315) # Enable
localtxt316   = language(30316) # Disable
localtxt317   = language(30317) # Enabled
localtxt318   = language(30318) # Disabled
localtxt319   = language(30319) # Wrong
localtxt320   = language(30320) # Reset All SkinSettings To Default?
localtxt321   = language(30321) # Default SkinSetting Restored
localtxt322   = language(30322) # Installed
localtxt323   = language(30323) # Update XXX
localtxt324   = language(30324) # Takes approximately 5 minutes
localtxt325   = language(30325) # Updating Repos
localtxt326   = language(30326) # Updating Addons
localtxt327   = language(30327) # Nothing Changed

ADDONS = [
  ["3XZ", "plugin.video.adult.3xz"],
  ["Adult's Only HUB", "plugin.video.aob"],
  ["Beeg.com", "plugin.video.beeg.com"],
  ["Cherry Pie", "plugin.video.cherrypie"],
  ["Empflix", "plugin.video.empflix"],
  ["ePornik", "plugin.video.epornik"],
  ["Erotic Shark", "plugin.video.eroticshark"],
  ["Erotik", "plugin.video.erotik"],
  ["FantastiCC", "plugin.video.fantasticc"],
  ["Kindgirls", "plugin.image.kindgirls"],
  ["Korean XXX", "plugin.video.korea-xxx"],
  ["LubeTube", "plugin.video.lubetube"],
  ["Porn Hub", "plugin.video.pornhub"],
  ["RedTube", "plugin.video.redtube"],
  ["Tube8", "plugin.video.tube8"],
  ["Ultimate Whitecream", "plugin.video.uwc"],
  ["VideoDevil", "plugin.video.videodevil"],
  ["Wood Rocket", "plugin.video.woodrocket"],
  ["xHamster Gay", "plugin.video.xhamstergay"],
  ["YouJizz.com", "plugin.video.you.jizz"],
  ["Youporn Gay", "plugin.video.youporngay"]
]

REPOS = [
  ["achilles addons", "repository.googlecode.achilles-projects"],
  ["anonymous repo adults", "repository.anonymous.adults"],
  ["IPTVxtra XBMC Add-ons", "repository.iptvxtra"],
  ["MisterX Repository", "repository.MisterX"],
  ["smokdpi's Add-ons", "repository.smokdpi"],
  ["Whitecream Repository", "repository.whitecream"],
  ["XBMC-Adult Addons", "repository.xbmcadult"]
]

prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass

def XxxOn():
    if dialog.yesno(localtxt0, 'Log On?',):
        for channel in ADDONS:
            sourcepath=xbmc.translatePath(os.path.join('special://home/addons/plugin.program.openeleq.tools/resources/xxx/',channel[1]))
            destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
            if os.path.exists(destpath)==False:
                shutil.copytree(sourcepath, destpath)
            else:
                pass
        for channel in REPOS:
            sourcepath=xbmc.translatePath(os.path.join('special://home/addons/plugin.program.openeleq.tools/resources/xxx/',channel[1]))
            destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
            if os.path.exists(destpath)==False:
                shutil.copytree(sourcepath, destpath)
            else:
                pass
        xbmc.executebuiltin("Notification(Password,Please, 5000, %s)" % (image))
        xbmc.executebuiltin("LoadProfile(Adult,prompt)")
        xbmc.executebuiltin("Notification(Logged,On, 5000, %s)" % (image))
    else:
        xbmc.executebuiltin("Notification(Log On,Cancelled, 5000, %s)" % (image))

#-------------------

def XxxOff():
    if dialog.yesno(localtxt0, 'Log Off?',):
        for channel in ADDONS:
            destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
            if os.path.exists(destpath)==True:
                shutil.rmtree(destpath)
            else:
                pass
        for channel in REPOS:
            destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
            if os.path.exists(destpath)==True:
                shutil.rmtree(destpath)
            else:
                pass
        xbmc.executebuiltin("Notification(Logging,Off, 5000, %s)" % (image))
        xbmc.executebuiltin("LoadProfile(Main,prompt)")
        xbmc.executebuiltin("Notification(Logged,Off, 5000, %s)" % (image))
    else:
        xbmc.executebuiltin("Notification(Log Off,Cancelled, 5000, %s)" % (image))

#-------------------

def XxxReset():
    if dialog.yesno(localtxt0, localtxt320+'?',):
        for channel in ADDONS:
            destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
            if os.path.exists(destpath)==True:
                shutil.rmtree(destpath)
            else:
                pass
        for channel in REPOS:
            destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
            if os.path.exists(destpath)==True:
                shutil.rmtree(destpath)
            else:
                pass
        xbmc.executebuiltin("Notification("+localtxt314+","+localtxt318+", 5000, %s)" % (image))
        xbmc.executebuiltin("Skin.SetString(Custom1HomeItem.Disable,True)")          
        xbmc.executebuiltin("Notification("+localtxt0+","+localtxt320+", 5000, %s)" % (image))
    else:
        xbmc.executebuiltin("Notification("+localtxt0+","+localtxt327+", 5000, %s)" % (image))

#-------------------

def XxxUpdate():
    if dialog.yesno(localtxt0, localtxt323+'? '+localtxt324+'...'):
        keyboard = xbmc.Keyboard()
        keyboard.setHeading(localtxt013)
        keyboard.doModal()
        if keyboard.isConfirmed():
            searcht=keyboard.getText()
            if searcht == password:
                for channel in ADDONS:
                    sourcepath=xbmc.translatePath(os.path.join('special://home/addons/plugin.program.openeleq.tools/resources/xxx/',channel[1]))
                    destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
                    if os.path.exists(destpath)==False:
                        shutil.copytree(sourcepath, destpath)
                    else:
                        pass
                for channel in REPOS:
                    sourcepath=xbmc.translatePath(os.path.join('special://home/addons/plugin.program.openeleq.tools/resources/xxx/',channel[1]))
                    destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
                    if os.path.exists(destpath)==False:
                        shutil.copytree(sourcepath, destpath)
                    else:
                        pass
                xbmc.executebuiltin("Notification("+localtxt314+","+localtxt317+", 5000, %s)" % (image))
                xbmc.executebuiltin("Notification("+localtxt314+","+localtxt317+", 5000, %s)" % (image))
                xbmc.executebuiltin("Notification("+localtxt0+","+localtxt325+", 5000, %s)" % (image))
                xbmc.executebuiltin("UpdateAddonRepos")
                time.sleep(30)
                xbmc.executebuiltin("Notification("+localtxt0+","+localtxt326+", 5000, %s)" % (image))
                xbmc.executebuiltin("UpdateLocalAddons")
                time.sleep(300)
                xbmc.executebuiltin("Notification("+localtxt323+","+localtxt313+", 5000, %s)" % (image))
                for channel in ADDONS:
                    sourcepath=xbmc.translatePath(os.path.join('special://home/addons/plugin.program.openeleq.tools/resources/xxx/',channel[1]))
                    destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
                    if os.path.exists(sourcepath)==True and os.path.exists(destpath)==True:
                        shutil.rmtree(sourcepath)					
                        shutil.copytree(destpath, sourcepath)
                    else:
                        pass
                for channel in REPOS:
                    sourcepath=xbmc.translatePath(os.path.join('special://home/addons/plugin.program.openeleq.tools/resources/xxx/',channel[1]))
                    destpath=xbmc.translatePath(os.path.join('special://home/addons/',channel[1]))
                    if os.path.exists(sourcepath)==True and os.path.exists(destpath)==True:
                        shutil.rmtree(sourcepath)					
                        shutil.copytree(destpath, sourcepath)
                        shutil.rmtree(destpath)					
                    else:
                        pass
                xbmc.executebuiltin("Notification("+localtxt326+","+localtxt313+", 5000, %s)" % (image))
            else:
                xbmc.executebuiltin("Notification("+localtxt319+","+localtxt013+", 5000, %s)" % (image))
    else:
        xbmc.executebuiltin("Notification("+localtxt314+","+localtxt327+", 5000, %s)" % (image))

#-------------------

if prnum == 'xxxon':
    XxxOn()

elif prnum == 'xxxoff':
    XxxOff()

elif prnum == 'xxxreset':
    XxxReset()
	
elif prnum == 'xxxupdate':
    XxxUpdate()
	
else:
    print 'INVALID ARGUMENT'