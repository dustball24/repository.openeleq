# -*- coding: utf-8 -*-
'''
    Torrenter v2 plugin for XBMC/Kodi
    Copyright (C) 2012-2015 Vadim Skorba v1 - DiMartino v2
    http://forum.kodi.tv/showthread.php?tid=214366

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import thread
import os
import urllib2
import hashlib
import re
from StringIO import StringIO
import gzip
import sys

import xbmc
import xbmcgui
import xbmcvfs
import Localization
from functions import file_encode, isSubtitle, DownloadDB, log, debug, is_writable
from platform_pulsar import get_platform

class Libtorrent:
    magnetLink = None
    startPart = 0
    endPart = 0
    partOffset = 0
    torrentHandle = None
    session = None
    downloadThread = None
    threadComplete = False
    lt = None
    save_resume_data = None

    def __init__(self, storageDirectory='', torrentFile='', torrentFilesDirectory='torrents'):
        self.platform = get_platform()
        self.storageDirectory = storageDirectory
        self.torrentFilesPath = os.path.join(self.storageDirectory, torrentFilesDirectory) + os.sep
        if not is_writable(self.storageDirectory):
            xbmcgui.Dialog().ok(Localization.localize('Torrenter v2'),
                    Localization.localize('Your storage path is not writable or not local! Please change it in settings!'),
                    Localization.localize(self.storageDirectory))

            sys.exit(1)

        try:
            from python_libtorrent import get_libtorrent
            libtorrent=get_libtorrent()
            log('Imported libtorrent v%s from python_libtorrent/%s' %(libtorrent.version, self.platform['system']))
            module=True
        except Exception, e:
            module=False
            log('Error importing python_libtorrent.%s. Exception: %s' %(self.platform['system'], str(e)))
            import libtorrent

        try:
            if not module: log('Imported libtorrent v' + libtorrent.version + ' from system')
            self.lt = libtorrent
            del libtorrent

        except Exception, e:
            log('Error importing from system. Exception: ' + str(e))
            xbmcgui.Dialog().ok(Localization.localize('Python-Libtorrent Not Found'),
                                Localization.localize(self.platform["message"][0]),
                                Localization.localize(self.platform["message"][1]))
            return

        if xbmcvfs.exists(torrentFile):
            self.torrentFile = torrentFile
            e=self.lt.bdecode(xbmcvfs.File(self.torrentFile,'rb').read())
            self.torrentFileInfo = self.lt.torrent_info(e)
        elif re.match("^magnet\:.+$", torrentFile):
            self.magnetLink = torrentFile

    def saveTorrent(self, torrentUrl):
        if re.match("^magnet\:.+$", torrentUrl):
            self.magnetLink = torrentUrl
            self.magnetToTorrent(torrentUrl)
            self.magnetLink = None
            return self.torrentFile
        else:
            if not xbmcvfs.exists(self.torrentFilesPath):
                xbmcvfs.mkdirs(self.torrentFilesPath)
            torrentFile = self.torrentFilesPath + self.md5(
                torrentUrl) + '.torrent'
            try:
                if not re.match("^http\:.+$", torrentUrl):
                    content = xbmcvfs.File(torrentUrl, "rb").read()
                else:
                    request = urllib2.Request(torrentUrl)
                    request.add_header('Referer', torrentUrl)
                    request.add_header('Accept-encoding', 'gzip')
                    result = urllib2.urlopen(request)
                    if result.info().get('Content-Encoding') == 'gzip':
                        buf = StringIO(result.read())
                        f = gzip.GzipFile(fileobj=buf)
                        content = f.read()
                    else:
                        content = result.read()

                localFile = xbmcvfs.File(torrentFile, "w+b")
                localFile.write(content)
                localFile.close()
            except Exception, e:
                log('Unable to save torrent file from "' + torrentUrl + '" to "' + torrentFile + '" in Torrent::saveTorrent' + '. Exception: ' + str(e))
                return
            if xbmcvfs.exists(torrentFile):
                try:
                    e=self.lt.bdecode(xbmcvfs.File(torrentFile,'rb').read())
                    self.torrentFileInfo = self.lt.torrent_info(e)
                except Exception, e:
                    log('Exception: ' + str(e))
                    xbmcvfs.delete(torrentFile)
                    return
                baseName = file_encode(os.path.basename(self.getFilePath()))
                if not xbmcvfs.exists(self.torrentFilesPath):
                    xbmcvfs.mkdirs(self.torrentFilesPath)
                newFile = self.torrentFilesPath + self.md5(baseName) + '.' + self.md5(
                    torrentUrl) + '.torrent'  # + '.'+ baseName
                if xbmcvfs.exists(newFile):
                    xbmcvfs.delete(newFile)
                if not xbmcvfs.exists(newFile):
                    try:
                        xbmcvfs.rename(torrentFile, newFile)
                    except Exception, e:
                        print 'Unable to rename torrent file from "' + torrentFile + '" to "' + newFile + '" in Torrent::renameTorrent' + '. Exception: ' + str(
                            e)
                        return
                self.torrentFile = newFile
                if not self.torrentFileInfo:
                    e=self.lt.bdecode(xbmcvfs.File(self.torrentFile,'rb').read())
                    self.torrentFileInfo = self.lt.torrent_info(e)
                return self.torrentFile

    def getMagnetInfo(self):
        magnetSettings = {
            'url': self.magnetLink,
            'save_path': self.storageDirectory,
            'storage_mode': self.lt.storage_mode_t(0),
            'paused': True,
            #'auto_managed': True,
            #'duplicate_is_error': True
        }
        progressBar = xbmcgui.DialogProgress()
        progressBar.create(Localization.localize('Please Wait'), Localization.localize('Magnet-link is converting'))
        #try:
        self.torrentHandle = self.session.add_torrent(magnetSettings)
        #except:
        #    self.torrentHandle = self.lt.add_magnet_uri(self.session, self.magnetLink, magnetSettings)
        iterator = 0
        while iterator < 100:
            xbmc.sleep(500)
            self.torrentHandle.force_dht_announce()
            progressBar.update(iterator, Localization.localize('Please Wait'), Localization.localize('Magnet-link is converting')+'.' * (iterator % 4), ' ')
            iterator += 1
            if progressBar.iscanceled():
                progressBar.update(0)
                progressBar.close()
                return
            if self.torrentHandle.status().has_metadata:
                iterator = 100
        progressBar.update(0)
        progressBar.close()
        if self.torrentHandle.status().has_metadata:
            try:
                info = self.torrentHandle.torrent_file()
            except:
                info = self.torrentHandle.get_torrent_info()
            return info

    def magnetToTorrent(self, magnet):
        self.magnetLink = magnet
        self.initSession()
        torrentInfo = self.getMagnetInfo()
        if torrentInfo:
            try:
                torrentFile = self.lt.create_torrent(torrentInfo)
                baseName = os.path.basename(self.storageDirectory + os.sep + torrentInfo.files()[0].path)
                if not xbmcvfs.exists(self.torrentFilesPath):
                    xbmcvfs.mkdirs(self.torrentFilesPath)
                self.torrentFile = self.torrentFilesPath + self.md5(baseName) + '.torrent'
                torentFileHandler = xbmcvfs.File(self.torrentFile, "w+b")
                torentFileHandler.write(self.lt.bencode(torrentFile.generate()))
                torentFileHandler.close()
                e=self.lt.bdecode(xbmcvfs.File(self.torrentFile,'rb').read())
                self.torrentFileInfo = self.lt.torrent_info(e)
            except:
                xbmc.executebuiltin("Notification(%s, %s, 7500)" % (Localization.localize('Error'), Localization.localize(
                    'Can\'t download torrent, probably no seeds available.')))
                self.torrentFileInfo = torrentInfo
            finally:
                self.session.remove_torrent(self.torrentHandle)
                self.torrentHandle = None

    def getUploadRate(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().upload_payload_rate

    def getDownloadRate(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().download_payload_rate

    def getPeers(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().num_peers

    def getSeeds(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().num_seeds

    def getFileSize(self, contentId=0):
        return self.getContentList()[contentId]['size']

    def getFilePath(self, contentId=0):
        return os.path.join(self.storageDirectory, self.getContentList()[contentId]['title'])  # .decode('utf8')

    def getContentList(self):
        filelist = []
        for contentId, contentFile in enumerate(self.torrentFileInfo.files()):
            stringdata = {"title": contentFile.path, "size": contentFile.size, "ind": int(contentId),
                          'offset': contentFile.offset}
            filelist.append(stringdata)
        return filelist

    def getSubsIds(self, filename):
        subs = []
        for i in self.getContentList():
            if isSubtitle(filename, i['title']):
                subs.append((i['ind'], i['title']))
        return subs

    def setUploadLimit(self, bytesPerSecond):
        try:
            session_settings = self.session.get_settings()
            session_settings['upload_rate_limit'] = int(bytesPerSecond)
            self.session.set_settings(session_settings)
        except:
            #0.16 compatibility
            self.session.set_upload_rate_limit(int(bytesPerSecond))

    def setDownloadLimit(self, bytesPerSecond):
        try:
            session_settings = self.session.get_settings()
            session_settings['download_rate_limit'] = int(bytesPerSecond)
            self.session.set_settings(session_settings)
        except:
            #0.16 compatibility
            self.session.set_download_rate_limit(int(bytesPerSecond))

    def md5(self, string):
        hasher = hashlib.md5()
        try:
            hasher.update(string)
        except:
            hasher.update(string.encode('utf-8', 'ignore'))
        return hasher.hexdigest()

    def downloadProcess(self, contentId, encrytion=True):
        self.initSession()
        if encrytion:
            self.encryptSession()
        self.startSession()
        self.paused = False
        db = DownloadDB()
        ContentList = self.getContentList()
        if contentId != None: contentId = int(contentId)
        if len(ContentList) == 1 or contentId not in [None, -1]:
            if not contentId: contentId = 0
            title = os.path.basename(ContentList[contentId]['title'])
            path = os.path.join(self.storageDirectory, ContentList[contentId]['title'])
            type = 'file'
        else:
            contentId = -1
            title = ContentList[0]['title'].split('\\')[0]
            path = os.path.join(self.storageDirectory, title)
            type = 'folder'

        add = db.add(title, path, type, {'progress': 0}, 'downloading', self.torrentFile, contentId,
                     self.storageDirectory)
        get = db.get(title)
        if add or get[5] == 'stopped':
            if get[5] == 'stopped':
                db.update_status(get[0], 'downloading')
            if contentId not in [None, -1]:
                self.continueSession(int(contentId), Offset=0, seeding=False)
            else:
                for i in range(self.torrentFileInfo.num_pieces()):
                    self.torrentHandle.piece_priority(i, 6)
            thread.start_new_thread(self.downloadLoop, (title,))

    def downloadLoop(self, title):
        db = DownloadDB()
        status = 'downloading'
        while db.get(title) and status != 'stopped':
            xbmc.sleep(3000)
            status = db.get_status(title)
            if not self.paused:
                if status == 'pause':
                    self.paused = True
                    self.session.pause()
            else:
                if status != 'pause':
                    self.paused = False
                    self.session.resume()
            s = self.torrentHandle.status()
            info = {}
            info['upload'] = s.upload_payload_rate
            info['download'] = s.download_payload_rate
            info['peers'] = s.num_peers
            info['seeds'] = s.num_seeds
            iterator = int(s.progress * 100)
            info['progress'] = iterator
            db.update(title, info)
            self.debug()
        self.session.remove_torrent(self.torrentHandle)
        return

    def initSession(self):
        self.session = self.lt.session()
        self.session.set_alert_mask(self.lt.alert.category_t.error_notification | self.lt.alert.category_t.status_notification | self.lt.alert.category_t.storage_notification)
        #self.session.set_alert_mask(self.lt.alert.category_t.all_categories)
        self.session.add_dht_router("router.bittorrent.com", 6881)
        self.session.add_dht_router("router.utorrent.com", 6881)
        self.session.start_dht()
        self.session.start_lsd()
        self.session.start_upnp()
        self.session.start_natpmp()
        try:
            self.session.listen_on(6881, 6891)
        except:
            log('listen_on(6881, 6891) error')

        #tribler example never tested
        #self.session.set_severity_level(self.lt.alert.severity_levels.info)
        #self.session.add_extension("ut_pex")
        #self.session.add_extension("lt_trackers")
        #self.session.add_extension("metadata_transfer")
        #self.session.add_extension("ut_metadata")
        # Ban peers that sends bad data
        #self.session.add_extension("smart_ban")

        # Session settings
        try:
            session_settings = self.session.get_settings()
            #
            session_settings['announce_to_all_tiers'] = True
            session_settings['announce_to_all_trackers'] = True
            session_settings['connection_speed'] = 100
            session_settings['peer_connect_timeout'] = 2
            session_settings['rate_limit_ip_overhead'] = True
            session_settings['request_timeout'] = 1
            session_settings['torrent_connect_boost'] = 100
            session_settings['user_agent'] = 'uTorrent/2200(24683)'
            #session_settings['cache_size'] = 0
            #session_settings['use_read_cache'] = False

        except:
            #0.15 compatibility
            log('[initSession]: Session settings 0.15 compatibility')
            session_settings = self.session.settings()

            session_settings.announce_to_all_tiers = True
            session_settings.announce_to_all_trackers = True
            session_settings.connection_speed = 100
            session_settings.peer_connect_timeout = 2
            session_settings.rate_limit_ip_overhead = True
            session_settings.request_timeout = 1
            session_settings.torrent_connect_boost = 100
            session_settings.user_agent = 'uTorrent/2200(24683)'
        #
        self.session.set_settings(session_settings)

    def encryptSession(self):
        # Encryption settings
        log('Encryption enabling...')
        try:
            encryption_settings = self.lt.pe_settings()
            encryption_settings.out_enc_policy = self.lt.enc_policy(self.lt.enc_policy.forced)
            encryption_settings.in_enc_policy = self.lt.enc_policy(self.lt.enc_policy.forced)
            encryption_settings.allowed_enc_level = self.lt.enc_level.both
            encryption_settings.prefer_rc4 = True
            self.session.set_pe_settings(encryption_settings)
            log('Encryption on!')
        except Exception, e:
            log('Encryption failed! Exception: ' + str(e))
            pass

    def startSession(self):
        if self.magnetLink:
            self.torrentFileInfo = self.getMagnetInfo()
        torrent_info={'ti': self.torrentFileInfo,
                      'save_path': self.storageDirectory,
                      'flags': 0x300,
                       #'storage_mode': self.lt.storage_mode_t(1),
                       'paused': False,
                       #'auto_managed': False,
                       #'duplicate_is_error': True
                      }
        self.torrentHandle = self.session.add_torrent(torrent_info)

        self.torrentHandle.set_sequential_download(True)
        self.torrentHandle.set_max_connections(60)
        self.torrentHandle.set_max_uploads(-1)
        self.stopSession()

    def stopSession(self):
        for i in range(self.torrentFileInfo.num_pieces()):
            self.torrentHandle.piece_priority(i, 0)

    def continueSession(self, contentId=0, Offset=0, seeding=False, isMP4=False):
        self.piece_length = self.torrentFileInfo.piece_length()
        selectedFileInfo = self.getContentList()[contentId]
        if not Offset:
            Offset = selectedFileInfo['size'] / (1024 * 1024)
        self.partOffset = (Offset * 1024 * 1024 / self.piece_length) + 1
        # print 'partOffset ' + str(self.partOffset)+str(' ')
        self.startPart = selectedFileInfo['offset'] / self.piece_length
        self.endPart = int((selectedFileInfo['offset'] + selectedFileInfo['size']) / self.piece_length)
        # print 'part ' + str(self.startPart)+ str(' ')+ str(self.endPart)
        multiplier = self.partOffset / 5
        log('continueSession: multiplier ' + str(multiplier))
        for i in range(self.startPart, self.startPart + self.partOffset):
            if i <= self.endPart:
                self.torrentHandle.piece_priority(i, 7)
                if isMP4 and i % multiplier == 0:
                    self.torrentHandle.piece_priority(self.endPart - i / multiplier, 7)
                    # print str(i)
                if multiplier >= i:
                    self.torrentHandle.piece_priority(self.endPart - i, 7)
                    # print str(i)

    def checkThread(self):
        if self.threadComplete == True:
            log('checkThread KIIIIIIIIIIILLLLLLLLLLLLLLL')
            try:
                self.session.remove_torrent(self.torrentHandle)
            except:
                log('RuntimeError: invalid torrent handle used')
            self.session.stop_natpmp()
            self.session.stop_upnp()
            self.session.stop_lsd()
            self.session.stop_dht()

    def debug(self):
        #try:
        if 1==1:
            # print str(self.getFilePath(0))
            s = self.torrentHandle.status()
            #get_cache_status=self.session.get_cache_status()
            #log('get_cache_status - %s/%s' % (str(get_cache_status.blocks_written), str(get_cache_status.blocks_read)))
            # get_settings=self.torrentHandle.status
            # print s.num_pieces
            #priorities = self.torrentHandle.piece_priorities()
            #print str(priorities)

            state_str = ['queued', 'checking', 'downloading metadata',
                         'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
            log('[%s] %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                  (self.lt.version, s.progress * 100, s.download_rate / 1000,
                   s.upload_rate / 1000, s.num_peers, state_str[s.state]))
            #log('%s %s' % (self.get_debug_info('dht_state'), self.get_debug_info('trackers_sum')))
            #debug('TRACKERS:' +str(self.torrentHandle.trackers()))

            #received=self.session.pop_alert()
            #while received:
            #    debug('[debug]: ['+str(type(received))+'] the alert '+str(received)+' is received')
            #    #if type(received) == self.lt.torrent_finished_alert:
            #    #    self.session.pause()
            #    received = self.session.pop_alert()

            #log('is_dht_running:' +str(self.session.is_dht_running()))
            #log('dht_state:' +str(self.session.dht_state()))
            #i = 0
            # for t in s.pieces:
            #    if t: i=i+1
            #print str(self.session.pop_alert())
            # print str(s.pieces[self.startPart:self.endPart])
            # print 'True pieces: %d' % i
            # print s.current_tracker
            # print str(s.pieces)
        #except:
        else:
            log('debug error')
            pass

    def get_debug_info(self, info):
        result=''
        if info in ['trackers_full','trackers_sum']:
            trackers=[]
            for tracker in self.torrentHandle.trackers():
                trackers.append((tracker['url'], tracker['fails'], tracker['verified']))
            if info=='trackers_full':
                for url, fails, verified in trackers:
                    result=result+'%s: f=%d, v=%s' %(url, fails, str(verified))
            if info=='trackers_sum':
                fails_sum, verified_sum = 0, 0
                for url, fails, verified in trackers:
                    fails_sum+=fails
                    if verified: verified_sum+=1
                result=result+'Trackers: verified %d/%d, fails=%d' %(verified_sum, len(trackers)-1, fails_sum)
        if info=='dht_state':
            is_dht_running='ON' if self.session.is_dht_running() else 'OFF'
            try:
                nodes=self.session.dht_state().get('nodes')
            except:
                nodes=None
            nodes=len(nodes) if nodes else 0
            result='DHT: %s (%d)' % (is_dht_running, nodes)
        return result

    def dump(self, obj):
        for attr in dir(obj):
            try:
                log("'%s':'%s'," % (attr, getattr(obj, attr)))
            except:
                pass
