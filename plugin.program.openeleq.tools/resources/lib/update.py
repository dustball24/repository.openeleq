import xbmc, xbmcgui
import shutil
import urllib2,urllib
import os
import xbmcaddon

addon = xbmcaddon.Addon('plugin.program.openeleq.tools')

localtxt00 = addon.getSetting('UpdateName')
updatefile = addon.getSetting('UpdateFile')
profile    = addon.getSetting('UpdateProfile')
lock       = addon.getSetting('ProfileLockUpdate')

localtxt01 = addon.getLocalizedString(30050) # Update
localtxt02 = addon.getLocalizedString(30051) # Downloading and Unpacking. Please Wait.
localtxt03 = addon.getLocalizedString(30052) # Downloaded: 
localtxt04 = addon.getLocalizedString(30053) # Download Cancelled
localtxt05 = addon.getLocalizedString(30054) # Updating
localtxt06 = addon.getLocalizedString(30055) # Succeeded

def DownloaderClass(url,dest):
    dp = xbmcgui.DialogProgress()
    dp.create(localtxt00,localtxt02,'')
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print localtxt03+str(percent)+'%'
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        print localtxt04 # need to get this part working
        dp.close()

class MyClass(xbmcgui.Window):
  def __init__(self):
    dialog = xbmcgui.Dialog()
    if dialog.yesno(localtxt00,localtxt01+' '+localtxt00+' ?'):
        url = updatefile
        path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
        lib=os.path.join(path, 'update.zip')
        DownloaderClass(url,lib)
        addonfolder = xbmc.translatePath(os.path.join('special://home',''))
        xbmc.executebuiltin("XBMC.Extract(%s,%s)"%(lib,addonfolder))
     
   	xbmc.executebuiltin("ReloadKeymaps")
   	xbmc.executebuiltin("ReloadSkin()")
   	if profile != '' and lock == 'false':
   	    xbmc.executebuiltin("LoadProfile("+profile+",)")
   	elif profile != '' and lock == 'true':
   	    xbmc.executebuiltin("LoadProfile("+profile+",prompt)")
   	else:
   	    pass
   	xbmc.executebuiltin("Notification("+localtxt00+","+localtxt01+" "+localtxt06+",5000,special://skin/icon.png)")
      
mydisplay = MyClass()
del mydisplay