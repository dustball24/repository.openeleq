import xbmc, xbmcgui
import shutil
import urllib2,urllib
import xbmcaddon
import os

addon = xbmcaddon.Addon('plugin.program.openeleq.tools')

def DownloaderClass(url,dest):
    dp = xbmcgui.DialogProgress()
    dp.create('XBMC voor Beginners','Update Downloaden en Uitpakken','')
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print Gedownload+' '+str(percent)+'%'
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        print 'Download Geannuleerd' # need to get this part working
        dp.close()

class MyClass(xbmcgui.Window):
  def __init__(self):
    dialog = xbmcgui.Dialog()
    if dialog.yesno('XBMC voor Beginners','Updaten?'):
        url = 'https://copy.com/bRhtjpoKXlC0Od0G'
        path = xbmc.translatePath(os.path.join('special://home/addons/','packages'))
        lib=os.path.join(path, 'UpdateBinners.zip')
        DownloaderClass(url,lib)
        folder = xbmc.translatePath(os.path.join('special://home',''))
        xbmc.executebuiltin("XBMC.Extract(%s,%s)"%(lib,folder))

   	xbmc.executebuiltin("LoadProfile(Master user,)")
   	xbmc.executebuiltin("Notification(XBMC voor Beginners,Update Geslaagd,5000,special://skin/icon.png)")
      
mydisplay = MyClass()
del mydisplay
