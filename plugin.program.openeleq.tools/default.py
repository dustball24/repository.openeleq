# This file is part of plugin.video.nederland24 ("Nederland24")

# Nederland24 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Nederland24 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Nederland24.  If not, see <http://www.gnu.org/licenses/>.


import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import urllib2
import re
import urlparse
import httplib
import time

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer

xbmc.log("plugin.program.openeleq.tools:: Starting Addon")

###
addon       = xbmcaddon.Addon()
favLocation = addon.getSetting('SuperFavourite location')
m3uLocation = addon.getSetting('Playlist location')
halow       = addon.getSetting('HalowTV')
addonId     = addon.getAddonInfo('id')
m3u_file    = xbmc.translatePath(os.path.join(m3uLocation, 'QTV.m3u'))
fav_file    = xbmc.translatePath(os.path.join(favLocation, 'favourites.xml'))
addonPath   = xbmcaddon.Addon('plugin.program.openeleq.tools').getAddonInfo("path")
skinimage   = os.path.join(xbmc.translatePath('special://skin'),'icon.png')
image       = os.path.join(addonPath,'icon.png')
language    = addon.getLocalizedString
dialog      = xbmcgui.Dialog()


localtxt204 = language(30204) # M3U Generator
localtxt209 = language(30209) # Fav Generator
localtxt313 = language(30313) # Done

pluginhandle = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.program.openeleq.tools')
xbmcplugin.setContent(pluginhandle, 'episodes')
#xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)  #enable for alphabetic listing
IMG_DIR = os.path.join(settings.getAddonInfo("path"),"resources", "media")

###
API_URL = 'http://ida.omroep.nl/aapi/?stream='
BASE_URL = 'http://livestreams.omroep.nl/'
#USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25'
REF_URL = 'http://www.npo.nl'
TOKEN_URL = 'http://ida.omroep.nl/npoplayer/i.js'

SATCHANNELS = [
  ["NPO 1", "NPO 1.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4142.m3u8", "Omschrijving", "NPO 1", "NPO"],
  ["NPO 2", "NPO 2.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4143.m3u8", "Omschrijving", "NPO 2", "NPO"],
  ["NPO 3", "NPO 3.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4144.m3u8", "Omschrijving", "NPO 3", "NPO"],
  ["RTL 4", "RTL 4.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4149.m3u8", "Omschrijving", "RTL 4", "NL COMMERCIEEL"],
  ["RTL 5", "RTL 5.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4150.m3u8", "Omschrijving", "RTL 5", "NL COMMERCIEEL"],
  ["NET 5", "NET 5.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4145.m3u8", "Omschrijving", "NET 5", "NL COMMERCIEEL"],
  ["SBS 6", "SBS 6.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4147.m3u8", "Omschrijving", "SBS 6", "NL COMMERCIEEL"],
  ["RTL 7", "RTL 7.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4151.m3u8", "Omschrijving", "RTL 7", "NL COMMERCIEEL"],
  ["RTL 8", "RTL 8.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4152.m3u8", "Omschrijving", "RTL 8", "NL COMMERCIEEL"],
  ["SBS 9", "SBS 9.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4148.m3u8", "Omschrijving", "SBS 9", "NL COMMERCIEEL"],
  ["HBO", "HBO.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4156.m3u8", "Omschrijving", "HBO", "NL ABO"],
  ["HBO 2", "HBO 2.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4157.m3u8", "Omschrijving", "HBO 2", "NL ABO"],
  ["HBO 3", "HBO 3.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4158.m3u8", "Omschrijving", "HBO 3", "NL ABO"],
  ["FOX", "FOX.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4134.m3u8", "Omschrijving", "FOX", "NL ABO"],
  ["FOX Life", "FOX Life.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4133.m3u8", "Omschrijving", "FOX Life", "NL ABO"],
  ["FILM1 Spotlight", "FILM1 Spotlight.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4135.m3u8", "Omschrijving", "FILM1 Spotlight", "NL ABO"],
  ["FILM1 Premiere", "FILM1 Premiere.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4162.m3u8", "Omschrijving", "FILM1 Premiere", "NL ABO"],
  ["FILM1 Comedy", "FILM1 Comedy.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4160.m3u8", "Omschrijving", "FILM1 Comedy", "NL ABO"],
  ["FILM1 Action", "FILM1 Action.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4159.m3u8", "Omschrijving", "FILM1 Action", "NL ABO"],
  ["Edge Sport", "Edge Sport.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4140.m3u8", "Omschrijving", "Edge Sport", "NL SPORT"],
  ["SPORT1 Select", "SPORT1 Select.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4166.m3u8", "Omschrijving", "SPORT1 Select", "NL SPORT"],
  ["SPORT1 Voetbal", "SPORT1 Voetbal.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "SPORT1 Voetbal", "NL SPORT"],
  ["SPORT1 Golf", "SPORT1 Golf.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4168.m3u8", "Omschrijving", "SPORT1 Golf", "NL SPORT"],
  ["FOX Sports 1", "FOX Sports 1.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4169.m3u8", "Omschrijving", "FOX Sports 1", "NL SPORT"],
  ["FOX Sports 2", "FOX Sports 2.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4170.m3u8", "Omschrijving", "FOX Sports 2", "NL SPORT"],
  ["FOX Sports 3", "FOX Sports 3.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4171.m3u8", "Omschrijving", "FOX Sports 3", "NL SPORT"],
  ["FOX Sports 4", "FOX Sports 4.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4172.m3u8", "Omschrijving", "FOX Sports 4", "NL SPORT"],
  ["FOX Sports 5", "FOX Sports 5.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4157.m3u8", "Omschrijving", "FOX Sports 5", "NL SPORT"],
  ["BABY TV", "BABY TV.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "BABY TV", "NL KIDS"],
  ["Disney Channel", "Disney Channel.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4141.m3u8", "Omschrijving", "Disney Channel", "NL KIDS"],
  ["Veronica", "Veronica.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4177.m3u8", "Omschrijving", "Veronica", "NL KIDS"],
  ["AT 5", "AT 5.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "AT 5", "NL REGIONAAL"], 
  ["GPTV", "GPTV.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "GPTV", "NL REGIONAAL"],
  ["N1", "N1.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "N1", "NL REGIONAAL"],
  ["RTVDrenthe", "rtvdrenthe.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4155.m3u8", "Omschrijving", "RTVDrenthe", "NL REGIONAAL"],
  ["Discovery", "Discovery.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "Discovery", "NL OVERIG"],
  ["Comedy Central", "Comedy Central.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "Comedy Central", "NL OVERIG"],
  ["24 Kitchen", "24 Kitchen.png", "http://portal.rapidiptv.com:8080/live/sozdar00/sozdar024/4167.m3u8", "Omschrijving", "24 Kitchen", "NL OVERIG"],]

CHANNELS = [
  ["Best 24", "best24.png", "live/npo/thematv/best24/best24.isml/best24.m3u8", "Best 24 brengt hoogtepunten uit zestig jaar televisiehistorie. Het is een feelgoodkanaal met 24 uur per dag de leukste, grappigste en meest spraakmakende programma's uit de Hilversumse schatkamer. Best 24: de schatkamer van de publieke omroep.", "Best 24"],
  ["Cultura 24", "cultura24.png", "live/npo/thematv/cultura24/cultura24.isml/cultura24.m3u8", "Dit is het 'cultuurkanaal van de Publieke Omroep' met de beste recente en oudere 'kunst en expressie' over verschillende onderwerpen. Klassieke muziek, dans, literatuur, theater, beeldende kunst, film 'Waar cultuur is, is Cultura 24'.", "Cultura"],
  ["Duurzaam 24", "duurzaam.png", "http://wowza3.newsbyte.nl/live/_definst_/drzm2_2/playlist.m3u8", "Duurzaam24 is een digitaal kanaal gefocust op duurzaamheid", "Duurzaam 24"],
  ["Holland Doc 24", "hollanddoc24.png", "live/npo/thematv/hollanddoc24/hollanddoc24.isml/hollanddoc24.m3u8", "Holland Doc 24 brengt op verschillende manieren en niveaus documentaires en reportages onder de aandacht. De programmering op Holland Doc 24 is gecentreerd rond wekelijkse thema's, die gerelateerd zijn aan de actualiteit, de programmering van documentairerubrieken, van culturele instellingen en festivals.", "Holland Doc"],
  ["Humor TV 24", "humortv24.png", "live/npo/thematv/humor24/humor24.isml/humor24.m3u8", "Humor TV 24 is een uitgesproken comedykanaal: een frisse, Nederlandse humorzender met hoogwaardige, grappige, scherpe, jonge, nieuwe, satirische, humoristische programma's.", "Humor TV"],
  ["Journaal 24", "journaal24.png", "live/npo/thematv/journaal24/journaal24.isml/journaal24.m3u8", "Via het themakanaal 'Journaal 24' kunnen de live televisieuitzendingen van het NOS Journaal worden gevolgd. De laatste Journaaluitzending wordt herhaald tot de volgende uitzending van het NOS Journaal.", "Journaal 24"],
  ["Politiek 24", "politiek24.png", "live/npo/thematv/politiek24/politiek24.isml/politiek24.m3u8", "Politiek 24 is het digitale kanaal over de Nederlandse politiek in de breedste zin van het woord.", "Politiek24"],
  ["Zappelin", "familie24.png", "live/npo/thematv/zappelin24/zappelin24.isml/zappelin24.m3u8", "Z@ppelin24 zendt dagelijks uit van half drie 's nachts tot half negen 's avonds. Familie24 is er op de tussenliggende tijd. Z@ppelin 24 biedt ruimte aan (oude) bekende peuterprogramma's en je kunt er kijken naar nieuwe kleuterseries. Op Familie24 zijn bekende programma's te zien en nieuwe programma's en documentaires die speciaal voor Familie24 zijn gemaakt of aangekocht.", "Zapp 24"],
  ["RTV Noord", "rtvnoord.png", "live/npo/regionaal/rtvnoord/rtvnoord.isml/rtvnoord.m3u8", "RTV Noord. Altijd op Noord.", "RTV Noord"],
  ["RTV Oost", "rtvoost.png", "live/regionaal/rtvoost/livestream1/livestream1.isml/livestream1.m3u8", "RTV Oost is het publieke regionale radio en televisiestation van Overijssel. Regionaal nieuws, sport en informatie vormen de hoofdmoot van de programma's, maar ook streekcultuur, muziek en ontspannende regionale programma's komen ruimschoots aan bod.", "RTV Oost"],
  ["RTV Utrecht", "rtvutrecht.png", "live/regionaal/rtvutrecht/rtvutrecht/rtvutrecht.isml/rtvutrecht.m3u8", "De regionale televisiezender brengt nieuws, achtergronden en informatie over de provincie Utrecht. Daarnaast is er ook aandacht voor sport, kunst, cultuur en natuur in de provincie.", "RTV Utrecht"],
  ["UStad", "ustad.png", "live/regionaal/rtvutrecht/ustad/ustad.isml/ustad.m3u8", "Televisie met nieuws, informatie en cultuur uit de stad Utrecht. Ook worden programma's uitgezonden die gemaakt zijn door studenten en bewoners.", "UStad"],
  ["Omrop Fryslan", "Omrop Fryslan.png", "http://live.wowza.kpnstreaming.nl/omropfryslanlive/OFstream04.smil/playlist.m3u8", "Televisie met nieuws, informatie en cultuur uit de stad Utrecht. Ook worden programma's uitgezonden die gemaakt zijn door studenten en bewoners.", "Omrop Fryslan"],
  ["OOG Radio TV", "OOG Radio.png", "http://live.streamone.nl/livestream/y2DmAqZZu8aa/playlist.m3u8", "OOG Radio TV", "OOG Radio TV"],
  ["Slingeland FM TV", "Slingeland FM.png", "http://live.streamone.nl/livestream/jL2CdF9ZzerQ/playlist.m3u8", "Radio Slingeland FM TV", "Slingeland FM TV"],
  ["Weert FM TV", "Weert FM.png", "http://live.streamone.nl/livestream/u2SioS02Af77/playlist.m3u8", "Weert FM TV", "Weert FM TV"],
  ["3FM", "3fm.png", "live/npo/visualradio/3fm/3fm.isml/3fm.m3u8", "3FM is altijd de eerste met nieuwe muziek, achtergronden, festivals en de beste DJ's.", "NPO 3FM"],
  ["FunX", "funx.png", "live/npo/visualradio/funx/funx.isml/funx.m3u8", "FunX is de publieke zender voor jongeren in de grote steden. De FunX DJ's draaien een aantrekkelijke mix van hiphop, RnB, dance, reggae en praten de luisteraar dagelijks bij over de actualiteit en entertainment. De zender doet verslag van relevante festivals en evenementen in de grote steden.", "FunX (kabel)"],
  ["Radio 1", "radio1.png", "live/npo/visualradio/radio1/radio1.isml/radio1.m3u8", "Radio 1 is de nieuws- en sportzender van de Nederlandse Publieke Omroep. Zeven dagen in de week, 24 uur per dag, de snelste nieuwsvoorziening in de ether en op de kabel.", "NPO Radio 1"],
  ["Radio 2", "radio2.png", "live/npo/visualradio/radio2/radio2.isml/radio2.m3u8", "Op Radio 2 hoor je het beste uit vijftig jaar popmuziek, afgewisseld met de actualiteit.", "NPO Radio 2"],
  ["Radio 538", "Radio 538 TV.png", "http://538hls.lswcdn.triple-it.nl/content/538webcam/538webcam_0.m3u8", "Radio 538", "Radio 538"],
  ["Slam TV", "Slam! FM.png", "http://hls2.slamfm.nl/content/slamtv/slamtv_1.m3u8", "Slam TV", "Slam TV"],
]

TV24SAT = [
  ["101 TV", "101tv.png", "live/npo/thematv/101tv/101tv.isml/101tv.m3u8", "Weg met suffe en saaie tv! Het is tijd voor 101 TV, het 24-uurs jongerenkanaal van BNN en de Publieke Omroep. Met rauwe en brutale programma's, van en voor jongeren. Boordevol hilarische fragmenten, spannende livegames, bizarre experimenten en nieuws over festivals en gratis concertkaartjes. Kijken dus!", "101.TV", "NPO"],
  ["Best 24", "best24.png", "live/npo/thematv/best24/best24.isml/best24.m3u8", "Best 24 brengt hoogtepunten uit zestig jaar televisiehistorie. Het is een feelgoodkanaal met 24 uur per dag de leukste, grappigste en meest spraakmakende programma's uit de Hilversumse schatkamer. Best 24: de schatkamer van de publieke omroep.", "Best 24", "NPO"],
  ["Cultura 24", "cultura24.png", "live/npo/thematv/cultura24/cultura24.isml/cultura24.m3u8", "Dit is het 'cultuurkanaal van de Publieke Omroep' met de beste recente en oudere 'kunst en expressie' over verschillende onderwerpen. Klassieke muziek, dans, literatuur, theater, beeldende kunst, film 'Waar cultuur is, is Cultura 24'.", "Cultura", "NPO"],
  ["Holland Doc 24", "hollanddoc24.png", "live/npo/thematv/hollanddoc24/hollanddoc24.isml/hollanddoc24.m3u8", "Holland Doc 24 brengt op verschillende manieren en niveaus documentaires en reportages onder de aandacht. De programmering op Holland Doc 24 is gecentreerd rond wekelijkse thema's, die gerelateerd zijn aan de actualiteit, de programmering van documentairerubrieken, van culturele instellingen en festivals.", "Holland Doc", "NPO"],
  ["Humor TV 24", "humortv24.png", "live/npo/thematv/humor24/humor24.isml/humor24.m3u8", "Humor TV 24 is een uitgesproken comedykanaal: een frisse, Nederlandse humorzender met hoogwaardige, grappige, scherpe, jonge, nieuwe, satirische, humoristische programma's.", "Humor TV", "NPO"],
  ["Journaal 24", "journaal24.png", "live/npo/thematv/journaal24/journaal24.isml/journaal24.m3u8", "Via het themakanaal 'Journaal 24' kunnen de live televisieuitzendingen van het NOS Journaal worden gevolgd. De laatste Journaaluitzending wordt herhaald tot de volgende uitzending van het NOS Journaal.", "Journaal 24", "NPO"],
  ["Politiek 24", "politiek24.png", "live/npo/thematv/politiek24/politiek24.isml/politiek24.m3u8", "Politiek 24 is het digitale kanaal over de Nederlandse politiek in de breedste zin van het woord.", "Politiek24", "NPO"],
  ["Zappelin", "familie24.png", "live/npo/thematv/zappelin24/zappelin24.isml/zappelin24.m3u8", "Z@ppelin24 zendt dagelijks uit van half drie 's nachts tot half negen 's avonds. Familie24 is er op de tussenliggende tijd. Z@ppelin 24 biedt ruimte aan (oude) bekende peuterprogramma's en je kunt er kijken naar nieuwe kleuterseries. Op Familie24 zijn bekende programma's te zien en nieuwe programma's en documentaires die speciaal voor Familie24 zijn gemaakt of aangekocht.", "Zapp 24", "NPO"],
  ["RTV Noord", "rtvnoord.png", "live/npo/regionaal/rtvnoord/rtvnoord.isml/rtvnoord.m3u8", "RTV Noord. Altijd op Noord.", "RTV Noord", "NL REGIONAAL"],
  ["RTV Oost", "rtvoost.png", "live/regionaal/rtvoost/livestream1/livestream1.isml/livestream1.m3u8", "RTV Oost is het publieke regionale radio en televisiestation van Overijssel. Regionaal nieuws, sport en informatie vormen de hoofdmoot van de programma's, maar ook streekcultuur, muziek en ontspannende regionale programma's komen ruimschoots aan bod.", "RTV Oost", "NL REGIONAAL"],
  ["RTV Utrecht", "rtvutrecht.png", "live/regionaal/rtvutrecht/rtvutrecht/rtvutrecht.isml/rtvutrecht.m3u8", "De regionale televisiezender brengt nieuws, achtergronden en informatie over de provincie Utrecht. Daarnaast is er ook aandacht voor sport, kunst, cultuur en natuur in de provincie.", "RTV Utrecht", "NL REGIONAAL"],
  ["UStad", "ustad.png", "live/regionaal/rtvutrecht/ustad/ustad.isml/ustad.m3u8", "Televisie met nieuws, informatie en cultuur uit de stad Utrecht. Ook worden programma's uitgezonden die gemaakt zijn door studenten en bewoners.", "UStad", "NL REGIONAAL"],
  ["3FM", "3fm.png", "live/npo/visualradio/3fm/3fm.isml/3fm.m3u8", "3FM is altijd de eerste met nieuwe muziek, achtergronden, festivals en de beste DJ's.", "NPO 3FM", "VISUAL RADIO"],
  ["FunX", "funx.png", "live/npo/visualradio/funx/funx.isml/funx.m3u8", "FunX is de publieke zender voor jongeren in de grote steden. De FunX DJ's draaien een aantrekkelijke mix van hiphop, RnB, dance, reggae en praten de luisteraar dagelijks bij over de actualiteit en entertainment. De zender doet verslag van relevante festivals en evenementen in de grote steden.", "FunX (kabel)", "VISUAL RADIO"],
  ["Radio 1", "radio1.png", "live/npo/visualradio/radio1/radio1.isml/radio1.m3u8", "Radio 1 is de nieuws- en sportzender van de Nederlandse Publieke Omroep. Zeven dagen in de week, 24 uur per dag, de snelste nieuwsvoorziening in de ether en op de kabel.", "NPO Radio 1", "VISUAL RADIO"],
  ["Radio 2", "radio2.png", "live/npo/visualradio/radio2/radio2.isml/radio2.m3u8", "Op Radio 2 hoor je het beste uit vijftig jaar popmuziek, afgewisseld met de actualiteit.", "NPO Radio 2", "VISUAL RADIO"],
]

TV24M3U = [
  ["NPO 1", "NPO 1.png", "live/npo/tvlive/ned1/ned1.isml/ned1.m3u8", "NPO 1 (tot 19 augustus 2014: Nederland 1) is een van de drie televisiezenders van de Nederlandse Publieke Omroep en is het oudste televisiekanaal van Nederland. Op NPO 1 worden programma's uitgezonden voor een breed publiek, zoals shows, spelletjes, series, drama en comedy. Verder is NPO 1 de calamiteitenzender. Wanneer er behoefte is aan een extra journaal voor bijvoorbeeld een ramp, dan zal dit plaatsvinden op NPO 1. Ook bijna alle bulletins van het NOS Journaal, de weekenduitzendingen van NOS Studio Sport en belangrijke evenementen (zoals Prinsjesdag, Koningsdag, de Algemene beschouwingen van de Tweede Kamer en sportevenementen als de Olympische Spelen en het WK Voetbal) worden via NPO 1 aangeboden.", "NPO 1", "Nl24 TV"],
  ["NPO 2", "NPO 2.png", "live/npo/tvlive/ned2/ned2.isml/ned2.m3u8", "NPO 2 (eerder Nederland 2 en TV 2) is een van de drie televisiezenders van de Nederlandse Publieke Omroep. De zender is in oktober 1964 opgericht en zou zich vanaf eind jaren tachtig vooral profileren als een zender met vooral veel sport, amusement en belangrijke evenementen. Tegenwoordig zijn deze onderdelen te vinden op NPO 1. NPO 2 profileert zich tegenwoordig als de 'verdiepende' zender, voor de 'geinteresseerde kijker'. Kunst, cultuur, politiek, samenleving en religie zijn vaste factoren voor NPO 2. NPO 2 is het thuisnet van programma's met een verdiepende grondslag. Veel van de programma's van de NTR, VPRO, NCRV, EO en de zogenaamde 2.42-omroepen zijn via dit net te volgen. Vaste onderdelen op NPO 2 zijn oa. Uitzending Gemist (met tussen 09:10 en 16:00 uur herhalingen van programma's van NPO 1, 2 en 3 van de afgelopen week), het 'actualiteitenuur' tussen 22:00 en 23:00 uur (met Nieuwsuur) en de nachtcaroussel met herhalingen van de actualiteitenrubrieken van de dag (met o.a. EenVandaag, Nieuwsuur). Op zaterdagochtend en -middag is het tijd voor programma's over cultuur en op zondag zijn er religieuze programma's en samenzang. Tijdens grote sportevenementen, zoals de Olympische Spelen, het EK voetbal en het WK voetbal worden alle journaals tijdelijk uitgezonden op NPO 2, zodat NPO 1 alle ruimte heeft om deze evenementen live uit te zenden.", "NPO 2", "Nl24 TV"],
  ["NPO 3", "NPO 3.png", "live/npo/tvlive/ned3/ned3.isml/ned3.m3u8", "NPO 3 (tot 19 augustus 2014: Nederland 3) is een van de drie televisiezenders van de Nederlandse Publieke Omroep. De officiele start van de zender was op 4 april 1988. Overdag wordt van 06.30 tot 19.30 uur op NPO 3 de kinderprogrammering van de NPO uitgezonden onder de namen Zappelin en Zapp. Hierbinnen worden ook de Schooltv-programma's voor peuters, kleuters en schoolkinderen op het basisonderwijs gerekend. Op maandag tot en met vrijdag om 19.30 uur start NPO 3 met haar uitzendingen, voor jongeren en jonge volwassenen. NPO 3 is naar eigen zeggen niet voorspelbaar en verschilt dan ook veel met de andere twee zenders van de NPO (NPO 1 en NPO 2). Het grote verschil tussen NPO 3 en de andere zenders van de publieke omroep is dat deze zender veel vernieuwing heeft in haar programmering. Sinds 2009 kent de zender 'de week van vernieuwing' met de naam 'TV Lab'. Daaruit kwamen programma's als Claudia op Vrijdag (VARA), Ik weet wat jij deed (TROS), De Bubbel (BNN) en Comedy Corner (NPS). Naast vernieuwing heeft Nederland 3 ook haar vaste programma's als Ranking the Stars (BNN), 71 graden Noord (AVRO), 3 op reis (LLINK-BNN), Spuiten & Slikken (BNN), Jong (EO), Puberruil (KRO) en Jan Smit, de zomer voorbij (TROS).", "NPO 3", "Nl24 TV"],
  ["101 TV", "101tv.png", "live/npo/thematv/101tv/101tv.isml/101tv.m3u8", "Weg met suffe en saaie tv! Het is tijd voor 101 TV, het 24-uurs jongerenkanaal van BNN en de Publieke Omroep. Met rauwe en brutale programma's, van en voor jongeren. Boordevol hilarische fragmenten, spannende livegames, bizarre experimenten en nieuws over festivals en gratis concertkaartjes. Kijken dus!", "101.TV", "Nl24 TV"],
  ["Best 24", "best24.png", "live/npo/thematv/best24/best24.isml/best24.m3u8", "Best 24 brengt hoogtepunten uit zestig jaar televisiehistorie. Het is een feelgoodkanaal met 24 uur per dag de leukste, grappigste en meest spraakmakende programma's uit de Hilversumse schatkamer. Best 24: de schatkamer van de publieke omroep.", "Best 24", "Nl24 TV"],
  ["Cultura 24", "cultura24.png", "live/npo/thematv/cultura24/cultura24.isml/cultura24.m3u8", "Dit is het 'cultuurkanaal van de Publieke Omroep' met de beste recente en oudere 'kunst en expressie' over verschillende onderwerpen. Klassieke muziek, dans, literatuur, theater, beeldende kunst, film 'Waar cultuur is, is Cultura 24'.", "Cultura", "Nl24 TV"],
  ["Holland Doc 24", "hollanddoc24.png", "live/npo/thematv/hollanddoc24/hollanddoc24.isml/hollanddoc24.m3u8", "Holland Doc 24 brengt op verschillende manieren en niveaus documentaires en reportages onder de aandacht. De programmering op Holland Doc 24 is gecentreerd rond wekelijkse thema's, die gerelateerd zijn aan de actualiteit, de programmering van documentairerubrieken, van culturele instellingen en festivals.", "Holland Doc", "Nl24 TV"],
  ["Humor TV 24", "humortv24.png", "live/npo/thematv/humor24/humor24.isml/humor24.m3u8", "Humor TV 24 is een uitgesproken comedykanaal: een frisse, Nederlandse humorzender met hoogwaardige, grappige, scherpe, jonge, nieuwe, satirische, humoristische programma's.", "Humor TV", "Nl24 TV"],
  ["Journaal 24", "journaal24.png", "live/npo/thematv/journaal24/journaal24.isml/journaal24.m3u8", "Via het themakanaal 'Journaal 24' kunnen de live televisieuitzendingen van het NOS Journaal worden gevolgd. De laatste Journaaluitzending wordt herhaald tot de volgende uitzending van het NOS Journaal.", "Journaal 24", "Nl24 TV"],
  ["Politiek 24", "politiek24.png", "live/npo/thematv/politiek24/politiek24.isml/politiek24.m3u8", "Politiek 24 is het digitale kanaal over de Nederlandse politiek in de breedste zin van het woord.", "Politiek24", "Nl24 TV"],
  ["Zappelin", "familie24.png", "live/npo/thematv/zappelin24/zappelin24.isml/zappelin24.m3u8", "Z@ppelin24 zendt dagelijks uit van half drie 's nachts tot half negen 's avonds. Familie24 is er op de tussenliggende tijd. Z@ppelin 24 biedt ruimte aan (oude) bekende peuterprogramma's en je kunt er kijken naar nieuwe kleuterseries. Op Familie24 zijn bekende programma's te zien en nieuwe programma's en documentaires die speciaal voor Familie24 zijn gemaakt of aangekocht.", "Zapp 24", "Nl24 TV"],
  ["RTV Noord", "rtvnoord.png", "live/npo/regionaal/rtvnoord/rtvnoord.isml/rtvnoord.m3u8", "RTV Noord. Altijd op Noord.", "RTV Noord", "Regio TV"],
  ["RTV Oost", "rtvoost.png", "live/regionaal/rtvoost/livestream1/livestream1.isml/livestream1.m3u8", "RTV Oost is het publieke regionale radio en televisiestation van Overijssel. Regionaal nieuws, sport en informatie vormen de hoofdmoot van de programma's, maar ook streekcultuur, muziek en ontspannende regionale programma's komen ruimschoots aan bod.", "RTV Oost", "Regio TV"],
  ["RTV Utrecht", "rtvutrecht.png", "live/regionaal/rtvutrecht/rtvutrecht/rtvutrecht.isml/rtvutrecht.m3u8", "De regionale televisiezender brengt nieuws, achtergronden en informatie over de provincie Utrecht. Daarnaast is er ook aandacht voor sport, kunst, cultuur en natuur in de provincie.", "RTV Utrecht", "Regio TV"],
  ["UStad", "ustad.png", "live/regionaal/rtvutrecht/ustad/ustad.isml/ustad.m3u8", "Televisie met nieuws, informatie en cultuur uit de stad Utrecht. Ook worden programma's uitgezonden die gemaakt zijn door studenten en bewoners.", "UStad", "Regio TV"],
  ["3FM", "3fm.png", "live/npo/visualradio/3fm/3fm.isml/3fm.m3u8", "3FM is altijd de eerste met nieuwe muziek, achtergronden, festivals en de beste DJ's.", "NPO 3FM", "Visual Radio"],
  ["FunX", "funx.png", "live/npo/visualradio/funx/funx.isml/funx.m3u8", "FunX is de publieke zender voor jongeren in de grote steden. De FunX DJ's draaien een aantrekkelijke mix van hiphop, RnB, dance, reggae en praten de luisteraar dagelijks bij over de actualiteit en entertainment. De zender doet verslag van relevante festivals en evenementen in de grote steden.", "FunX (kabel)", "Visual Radio"],
  ["Radio 1", "radio1.png", "live/npo/visualradio/radio1/radio1.isml/radio1.m3u8", "Radio 1 is de nieuws- en sportzender van de Nederlandse Publieke Omroep. Zeven dagen in de week, 24 uur per dag, de snelste nieuwsvoorziening in de ether en op de kabel.", "NPO Radio 1", "Visual Radio"],
  ["Radio 2", "radio2.png", "live/npo/visualradio/radio2/radio2.isml/radio2.m3u8", "Op Radio 2 hoor je het beste uit vijftig jaar popmuziek, afgewisseld met de actualiteit.", "NPO Radio 2", "Visual Radio"],
]

TVM3U = [
  ["1HD", "1HD.png", "rtmp://109.239.142.62/live/livestream3", "1HD", "1HD", "MUSIC TV"],
  ["AKA", "AKA.png", "http://rrr.sz.xlcdn.com/?account=AATW&file=akanew&type=live&service=wowza&protocol=http&output=playlist.m3u8", "AKA", "AKA", "MUSIC TV"],
  ["CapitalTV", "CapitalTV.png", "http://ooyalahd2-f.akamaihd.net/i/globalradio01_delivery@156521/index_656_av-p.m3u8", "CapitalTV", "CapitalTV", "MUSIC TV"],
  ["Cheerio", "Cheerio.png", "http://hls.novotelecom.ru/streaming/aone/tvrec/playlist.m3u8", "Cheerio", "Cheerio", "MUSIC TV"],
  ["DanceHD", "DanceHD.png", "rtmp://91.201.78.3:1935/live/dancehd", "DanceHD", "DanceHD", "MUSIC TV"],
  ["Djing DanceFloor", "Djing DanceFloor.png", "http://www.djing.com/tv/dancefloor.m3u8", "Djing DanceFloor", "Djing DanceFloor", "MUSIC TV"],
  ["Djing Hot", "Djing Hot.png", "http://www.djing.com/tv/hothothot.m3u8", "Djing Hot", "Djing Hot", "MUSIC TV"],
  ["Djing", "Djing.png", "http://cdn.djing.com/tv/d-03.m3u8", "Djing", "Djing", "MUSIC TV"],
  ["EskaBestMusic", "EskaBestMusic.png", "rtmp://stream.smcloud.net/live2/best/best_720p", "EskaBestMusic", "EskaBestMusic", "MUSIC TV"],
  ["EskaPartyTV", "EskaPartyTV.png", "rtmp://stream.smcloud.net/live2/eska_party/eska_party_360p", "EskaPartyTV", "EskaPartyTV", "MUSIC TV"],
  ["EskaRock", "EskaRock.png", "rtmp://stream.smcloud.net/live2/eska_rock/eska_rock_720p", "EskaRock", "EskaRock", "MUSIC TV"],
  ["EskaTV", "EskaTV.png", "rtmp://stream.smcloud.net/live/eskatv", "EskaTV", "EskaTV", "MUSIC TV"],
  ["JazzHD", "JazzHD.png", "rtmp://91.201.78.3:1935/live/jazzhd", "JazzHD", "JazzHD", "MUSIC TV"],
  ["KissTV", "KissTV.png", "http://kissfm.en-directo.com/iphone/index_multirate.m3u8", "KissTV", "KissTV", "MUSIC TV"],
  ["LiveHD", "LiveHD.png", "rtmp://91.201.78.3/live playpath=classicshd swfurl=http://www.livehd.tv/player/player.swf live=1 pageurl=http://www.livehd.tv/live.php?stream=classics&resolution=hd/?b?b*t$ token=6c69766568642e747620657374652063656c206d616920746172652121", "LiveHD", "LiveHD", "MUSIC TV"],
  ["Mezzo", "Mezzo.png", "http://hlsstr02.svc.iptv.rt.ru/hls/CH_MEZZO/variant.m3u8", "Mezzo", "Mezzo", "MUSIC TV"],
  ["MIX", "MIX.png", "rtmp://91.201.78.3/live playpath=onehdhd swfurl=http://www.livehd.tv/player/player.swf live=1 pageurl=http://www.livehd.tv/live.php?stream=livemix&resolution=hd/?b?b*t$ token=6c69766568642e747620657374652063656c206d616920746172652121", "MIX", "MIX", "MUSIC TV"],
  ["MTV Dance", "MTV Dance.png", "http://hlsstr02.svc.iptv.rt.ru/hls/CH_MTVDANCE/variant.m3u8", "MTV Dance", "MTV Dance", "MUSIC TV"],
  ["MTV Hits", "MTV Hits.png", "http://hlsstr02.svc.iptv.rt.ru/hls/CH_MTVHITS/variant.m3u8", "MTV Hits", "MTV Hits", "MUSIC TV"],
  ["MTV Rocks", "MTV Rocks.png", "http://hlsstr02.svc.iptv.rt.ru/hls/CH_MTVROCKS/variant.m3u8", "MTV Rocks", "MTV Rocks", "MUSIC TV"],
  ["NTWICM", "NTWICM.png", "http://rrr.sz.xlcdn.com/?account=AATW&file=nowmusic&type=live&service=wowza&protocol=http&output=playlist.m3u8", "NTWICM", "NTWICM", "MUSIC TV"],
  ["Omrop Fryslan", "Omrop Fryslan.png", "http://live.wowza.kpnstreaming.nl/omropfryslanlive/_definst_/OFstream04.smil/chunklist-b2000000.m3u", "Televisie met nieuws, informatie en cultuur uit de stad Utrecht. Ook worden programma's uitgezonden die gemaakt zijn door studenten en bewoners.", "Omrop Fryslan", "NL REGIONAAL"],
  ["OOG Radio TV", "OOG Radio.png", "http://live.streamone.nl/livestream/y2DmAqZZu8aa/playlist.m3u8", "OOG Radio TV", "OOG Radio TV", "NL REGIONAAL"],
  ["PlanetPop", "PlanetPop.png", "http://u.to/GC4bCg", "PlanetPop", "PlanetPop", "MUSIC TV"],
  ["PopHD", "PopHD.png", "rtmp://91.201.78.3:1935/live/pophd", "PopHD", "PopHD", "MUSIC TV"],
  ["Radio 538", "Radio 538 TV.png", "http://538hls.lswcdn.triple-it.nl/content/538webcam/538webcam_0.m3u8", "Radio 538", "Radio 538", "VISUAL RADIO"],
  ["RockHD", "RockHD.png", "rtmp://91.201.78.3:1935/live/rockhd", "RockHD", "RockHD", "MUSIC TV"],
  ["Slam TV", "Slam! FM.png", "http://hls2.slamfm.nl/content/slamtv/slamtv_1.m3u8", "Slam TV", "Slam TV", "VISUAL RADIO"],
  ["Slingeland FM TV", "Slingeland FM.png", "http://live.streamone.nl/livestream/jL2CdF9ZzerQ/playlist.m3u8", "Radio Slingeland FM TV", "Slingeland FM TV", "NL REGIONAAL"],
  ["SportTimeTV", "SportTimeTV.png", "http://streamer.a1.net/m3ugen/redundant/channels/Sporttime/SporttimeTV/channel1_1200.mp4", "SportTimeTV", "SportTimeTV", "MUSIC TV"],
  ["TraceUrban", "TraceUrban.png", "rtmp://58.97.57.152/live playpath=hd06 swfUrl=http://www.one2hd.com/swfs/mediaPlayer/mediaPlayer.swf pageUrl=http://www.one2hd.com/", "TraceUrban", "TraceUrban", "MUSIC TV"],
  ["VevoTV1", "VevoTV1.png", "http://vevoplaylist-live.hls.adaptive.level3.net/vevo/ch1/06/prog_index.m3u8", "VevoTV1", "VevoTV1", "MUSIC TV"],
  ["VevoTV2", "VevoTV2.png", "http://vevoplaylist-live.hls.adaptive.level3.net/vevo/ch2/06/prog_index.m3u8", "VevoTV2", "VevoTV2", "MUSIC TV"],
  ["VevoTV3", "VevoTV3.png", "http://vevoplaylist-live.hls.adaptive.level3.net/vevo/ch3/06/prog_index.m3u8", "VevoTV3", "VevoTV3", "MUSIC TV"],
  ["VH1", "VH1.png", "http://hlsstr02.svc.iptv.rt.ru/hls/CH_VH1EUROPEAN/variant.m3u8", "VH1", "VH1", "MUSIC TV"],
  ["VH1-Classic", "VH1-Classic.png", "http://hlsstr02.svc.iptv.rt.ru/hls/CH_VH1CLASSIC/variant.m3u8", "VH1-Classic", "VH1-Classic", "MUSIC TV"],
  ["Virgin", "Virgin.png", "rtmp://fms.105.net:1935/live/virgin1", "Virgin", "Virgin", "MUSIC TV"],
  ["VoxMusicTV", "VoxMusicTV.png", "rtmp://stream.smcloud.net/live2/vox/vox_720p", "VoxMusicTV", "VoxMusicTV", "MUSIC TV"],
  ["Weert FM TV", "Weert FM.png", "http://live.streamone.nl/livestream/u2SioS02Af77/playlist.m3u8", "Weert FM TV", "Weert FM TV", "NL REGIONAAL"],
]

RADIOM3U = [ 
  ["3FM", "3FMradio.png", "http://icecast.omroep.nl/3fm-bb-mp3", "Radio 3FM", "3FM", "NL NATIONAAL"],
  ["3FM Alternative", "3FM Alternative.png", "http://icecast.omroep.nl/3fm-alternative-mp3", "Radio 3FM Alternative", "3FM Alternative", "NL WEB RADIO"],
  ["3FM On Stage", "3FM On Stage.png", "http://icecast.omroep.nl/3fm-live-mp3", "Radio 3FM On Stage", "3FM On Stage", "NL WEB RADIO"],
  ["6 FM", "6 FM.png", "http://6fm.nl:8000", "Radio 6 FM", "6 FM", "NL REGIONAAL"],
  ["100% NL", "100% NL.png", "http://stream.100p.nl:8000/100pctnl.mp3", "100% NL", "100% NL", "NL NATIONAAL"],
  ["Accent FM", "Accent FM.png", "http://78.129.224.21:15402/", "Radio Accent FM", "Accent FM", "NL REGIONAAL"],
  ["Arrow Caz!", "Arrow Caz!.png", "http://81.23.251.71/Caz", "Radio Arrow Caz!", "Arrow Caz!", "NL NATIONAAL"],
  ["Arrow Classic Rock", "Arrow Classic Rock.png", "http://91.221.151.178:8109/", "Radio Arrow Classic Rock", "Arrow Classic Rock", "NL NATIONAAL"],
  ["Assen FM", "Assen FM.png", "http://icecast-origin.streamonecloud.net/zzg4KbMA8ERA", "Radio Assen FM", "Assen FM", "NL REGIONAAL"],
  ["Beyond The Beat Generation", "Beyond The Beat Generation.png", "http://82.148.208.55:8000/", "Radio Beyond The Beat Generation", "Beyond The Beat Generation", "NL REGIONAAL"],
  ["Bright FM Kids", "Bright FM Kids.png", "http://stream.hollanddata.eu/bfmkids-aacplus", "Radio Bright FM Kids", "Bright FM Kids", "NL WEB RADIO"],
  ["Bright FM", "Bright FM.png", "http://str1.hollanddata.eu/proxy/bright1?mp=/bfm-mp3", "Radio Bright FM", "Bright FM", "NL REGIONAAL"],
  ["Classic FM", "Classic FM.png", "http://8533.live.streamtheworld.com:443/CLASSICFM_SC", "Radio Classic FM", "Classic FM", "NL NATIONAAL"],
  ["Delta FM", "Delta FM.png", "http://stream1.icehosting.nl:8120/", "Radio Delta FM", "Delta FM", "NL REGIONAAL"],
  ["Dordrecht FM", "Dordrecht FM.png", "http://kippingmultimediaal.nl:8000/drechtstadfm.m3u", "Radio Dordrecht FM", "Dordrecht FM", "NL REGIONAAL"],
  ["Dordrechtstad FM", "Dordrechtstad FM.png", "http://78.157.223.11:8002", "Radio Dordrechtstad FM", "Dordrechtstad FM", "NL REGIONAAL"],
  ["Falcon FM", "Falcon FM.png", "http://server-16.stream-server.nl:8926/", "Radio Falcon FM", "Falcon FM", "NL REGIONAAL"],
  ["Groot Nieuws Radio", "Groot Nieuws Radio.png", "http://wms.streampartner.nl:8000/grootnieuwsradio", "Radio Groot Nieuws Radio", "Groot Nieuws Radio", "NL WEB RADIO"],
  ["Jouw FM", "Jouw FM.png", "http://stream.click2.nl:8058/", "Radio Jouw FM", "Jouw FM", "NL REGIONAAL"],
  ["Juize FM", "Juize FM.png", "http://538hls.lswcdn.triple-it.nl/content/juize/index.m3u8", "Radio Juize FM", "Juize FM", "NL NATIONAAL"],
  ["Keizerstad FM", "Keizerstad FM.png", "http://server-06.stream-server.nl:8800/", "Radio Keizerstad FM", "Keizerstad FM", "NL REGIONAAL"],
  ["L1", "L1.png", "http://icecast.omroep.nl/l1-radio-bb-mp3", "Radio L1", "L1", "NL REGIONAAL"],
  ["LekWaal FM", "LekWaal FM.png", "http://lekwaalfm.gkstreamen.nl:8040/", "Radio LekWaal FM", "LekWaal FM", "NL REGIONAAL"],
  ["M FM", "M FM.png", "http://81.173.3.140:80/", "Radio M FM", "M FM", "NL REGIONAAL"],
  ["Maasland FM", "Maasland FM.png", "http://icecast.streamone.nl/f5Snk8SjbA", "Radio Maasland FM", "Maasland FM", "NL REGIONAAL"],
  ["Nova Classic Rock", "Nova Classic Rock.png", "http://173.236.29.52:80/", "Radio Nova Classic Rock", "Nova Classic Rock", "NL REGIONAAL"],
  ["Omroep Brabant", "Omroep Brabant.png", "http://streaming.omroepbrabant.nl/mp3hq", "Radio Omroep Brabant", "Omroep Brabant", "NL REGIONAAL"],
  ["Omroep Flevoland", "Omroep Flevoland.png", "http://streams.omroepflevoland.nl:8000/flevoland64k", "Radio Omroep Flevoland", "Omroep Flevoland", "NL REGIONAAL"],
  ["Omroep Groesbeek", "Omroep Groesbeek.png", "http://icecast.omroepgroesbeek.nl:8000/live", "Radio Omroep Groesbeek", "Omroep Groesbeek", "NL REGIONAAL"],
  ["Omroep Landsmeer", "Omroep Landsmeer.png", "http://217.172.190.185:8092/;", "Radio Omroep Landsmeer", "Omroep Landsmeer", "NL REGIONAAL"],
  ["Omroep Reindonk", "Omroep Reindonk.png", "http://stream01.streamhier.nl:9702", "Radio Omroep Reindonk", "Omroep Reindonk", "NL REGIONAAL"],
  ["Omroep Venray", "Omroep Venray.png", "http://stream.omroepvenray.nl:8002/", "Radio Omroep Venray", "Omroep Venray", "NL REGIONAAL"],
  ["Omroep Zeeland", "Omroep Zeeland.png", "rtsp://livestream.zeelandnet.nl:554/live/omroepzeeland_radio_128k.sdp", "Radio Omroep Zeeland", "Omroep Zeeland", "NL REGIONAAL"],
  ["Omroep Zuidplas", "Omroep Zuidplas.png", "http://217.172.190.185:8016/", "Radio Omroep Zuidplas", "Omroep Zuidplas", "NL REGIONAAL"],
  ["Omrop Fryslan", "Omrop Fryslan.png", "http://icecast.pmedia70.kpnstreaming.nl/omropfryslanlive-OmropFryslanRadio.mp3", "Radio Omrop Fryslan", "Omrop Fryslan", "NL REGIONAAL"],
  ["OOG Radio", "OOG Radio.png", "http://live.streamone.nl/radiostream/u2HAq9DznBaa/playlist.m3u8", "Radio OOG Radio", "OOG Radio", "NL REGIONAAL"],
  ["Optimaal FM", "Optimaal FM.png", "http://radio.optimaal.fm:9000/", "Radio Optimaal FM", "Optimaal FM", "NL REGIONAAL"],
  ["Peel & Maas", "Peel & Maas.png", "http://icecast.streamone.nl:80/y2bXD9kGaq", "Radio Peel & Maas", "Peel & Maas", "NL REGIONAAL"],
  ["Pinguin Radio", "Pinguin Radio.png", "http://pr320.pinguinradio.nl:80/", "Pinguin Radio", "Pinguin Radio", "NL WEB RADIO"],
  ["Q-music", "Q-music.png", "http://icecast-qmusic.cdp.triple-it.nl/Qmusic_nl_live_96.mp3", "Radio Q-music", "Q-music", "NL NATIONAAL"],
  ["Radio 1", "Radio 1.png", "http://icecast.omroep.nl/radio1-bb-mp3", "Radio 1", "Radio 1", "NL NATIONAAL"],
  ["Radio 2", "Radio 2.png", "http://icecast.omroep.nl/radio2-bb-mp3", "Radio 2", "Radio 2", "NL NATIONAAL"],
  ["Radio 4", "Radio 4.png", "http://icecast.omroep.nl/radio4-bb-mp3", "Radio 4", "Radio 4", "NL NATIONAAL"],
  ["Radio 5", "Radio 5.png", "http://icecast.omroep.nl/radio5-bb-mp3", "Radio 5", "Radio 5", "NL NATIONAAL"],
  ["Radio 6", "Radio 6.png", "http://icecast.omroep.nl/radio6-bb-mp3", "Radio 6", "Radio 6", "NL NATIONAAL"],
  ["Radio 8 FM", "Radio 8 FM.png", "http://breedband.radio8fm.nl:8802/", "Radio 8 FM", "Radio 8 FM", "NL REGIONAAL"],
  ["Radio 10", "Radio 10.png", "http://stream.radio10.nl/radio10", "Radio 10", "Radio 10", "NL NATIONAAL"],
  ["Radio 538", "Radio 538.png", "http://vip-icecast.538.lw.triple-it.nl/RADIO538_MP3", "Radio 538", "Radio 538", "NL NATIONAAL"],
  ["Radio Almelo", "Radio Almelo.png", "http://lnx02.veldhovendesign.nl:8000/radioalmelo", "Radio Almelo", "Radio Almelo", "NL REGIONAAL"],
  ["Radio Beverwijk", "Radio Beverwijk.png", "http://stream.intronic.nl/beverwijk.m3u", "Radio Beverwijk", "Radio Beverwijk", "NL REGIONAAL"],
  ["Radio BNN", "Radio BNN.png", "http://icecast.omroep.nl:80/3fm-bnnfm-bb-mp3 ", "Radio Radio BNN", "Radio BNN", "NL WEB RADIO"],
  ["Radio Capelle", "Radio Capelle.png", "http://live.radiocapelle.nl:8000/", "Radio Capelle", "Radio Capelle", "NL REGIONAAL"],
  ["Radio Continu", "Radio Continu.png", "http://radiocontinu.ic-stream.nl:7062", "Radio Continu", "Radio Continu", "NL REGIONAAL"],
  ["Radio Drenthe", "Radio Drenthe.png", "http://stream.rtvdrenthe.nl:9001/RTVRadio", "Radio Drenthe", "Radio Drenthe", "NL REGIONAAL"],
  ["Radio Gelderland", "Radio Gelderland.png", "http://stream.omroepgelderland.nl/radiogelderland/pls.php", "Radio Gelderland", "Radio Gelderland", "NL REGIONAAL"],
  ["Radio Hengelo", "Radio Hengelo.png", "http://stream1.icehosting.nl:8128/", "Radio Radio Hengelo", "Radio Hengelo", "NL REGIONAAL"],
  ["Radio Hoeksche Waard", "Radio Hoeksche Waard.png", "http://icecast.streamone.nl/zzee82MDNSrR", "Radio Hoeksche Waard", "Radio Hoeksche Waard", "NL REGIONAAL"],
  ["Radio Holland Online", "Radio Holland Online.png", "http://stream.r-h-o.nl", "Radio Holland Online", "Radio Holland Online", "NL WEB RADIO"],
  ["Radio Hoorn", "Radio Hoorn.png", "http://stream1.musserver.nl:8002/;stream.mp3", "Radio Hoorn", "Radio Hoorn", "NL REGIONAAL"],
  ["Radio Ideaal", "Radio Ideaal.png", "http://live.streamone.nl/radiostream/zzWSyxykPk3Y/playlist.m3u8", "Radio Ideaal", "Radio Ideaal", "NL REGIONAAL"],
  ["Radio Kontakt", "Radio Kontakt.png", "http://88.159.163.202:8000/;?1429102516590.mp3", "Radio Kontakt", "Radio Kontakt", "NL REGIONAAL"],
  ["Radio M Utrecht", "Radio M Utrecht.png", "http://icecast.omroep.nl/rtvutrecht-radio-m-bb-mp3", "Radio M Utrecht", "Radio M Utrecht", "NL REGIONAAL"],
  ["Radio Maico", "Radio Maico.png", "http://server-09.stream-server.nl:8494", "Radio Maico", "Radio Maico", "NL REGIONAAL"],
  ["Radio Noordoost Friesland", "Radio Noordoost Friesland.png", "http://178.19.114.50:50004", "Radio Noordoost Friesland", "Radio Noordoost Friesland", "NL REGIONAAL"],
  ["Radio Nunspeet", "Radio Nunspeet.png", "http://37.59.195.28:8214/", "Radio Radio Nunspeet", "Radio Nunspeet", "NL REGIONAAL"],
  ["Radio Rijnmond", "Radio Rijnmond.png", "http://icecast.stream.bbvms.com/rijnmond-radio-mp3", "Radio Rijnmond", "Radio Rijnmond", "NL REGIONAAL"],
  ["Radio Schiedam", "Radio Schiedam.png", "http://icecast.streamone.nl:9029/stream", "Radio Schiedam", "Radio Schiedam", "NL REGIONAAL"],
  ["Radio Slotstad", "Radio Slotstad.png", "http://slotstad.live-streams.nl:8010/", "Radio Slotstad", "Radio Slotstad", "NL REGIONAAL"],
  ["Radio Veldhoven", "Radio Veldhoven.png", "http://88.159.59.242:8000/Veldhoven", "Radio Veldhoven", "Radio Veldhoven", "NL REGIONAAL"],
  ["Radio West", "Radio West.png", "http://icecast.stream.bbvms.com/omroepwest_radio_aac", "Radio West", "Radio West", "NL REGIONAAL"],
  ["Radio Westerwolde", "Radio Westerwolde.png", "http://178.19.114.74:6154/", "Radio Westerwolde", "Radio Westerwolde", "NL REGIONAAL"],
  ["Ram FM", "Ram FM.png", "http://uk1-vn.mixstream.net:9866", "Radio Ram FM", "Ram FM", "NL WEB RADIO"],
  ["Reformatorische Omroep", "Reformatorische Omroep.png", "http://media01.streampartner.nl:8003/live", "Radio Reformatorische Omroep", "Reformatorische Omroep", "NL WEB RADIO"],
  ["Seven FM", "Seven FM.png", "http://streams.seven.fm:8090/", "Radio Seven FM", "Seven FM", "NL WEB RADIO"],
  ["Skyline FM", "Skyline FM.png", "http://icecast.streamonecloud.net/zz5giI7VF5B6", "Radio Skyline FM", "Skyline FM", "NL REGIONAAL"],
  ["Skyradio", "Skyradio.png", "http://8533.live.streamtheworld.com:443/SKYRADIOAAC_SC", "Skyradio", "Skyradio", "NL NATIONAAL"],
  ["Slam! FM", "Slam! FM.png", "http://vip-icecast.538.lw.triple-it.nl:80/SLAMFM_MP3", "Radio Slam! FM", "Slam! FM", "NL NATIONAAL"],
  ["Slingeland FM", "Slingeland FM.png", "http://radiostream.rtvslingeland.nl/?1429100517554.mp3", "Radio Slingeland FM", "Slingeland FM", "NL REGIONAAL"],
  ["Smart FM", "Smart FM.png", "http://81.18.165.234:8361/", "Radio Smart FM", "Smart FM", "NL REGIONAAL"],
  ["Smelne", "Smelne.png", "mms://stream.smelnefm.nl/smelne", "Radio Smelne", "Smelne", "NL REGIONAAL"],
  ["Studio Brussel", "Studio Brussel.png", "http://mp3.streampower.be/stubru-high.mp3", "Radio Studio Brussel", "Studio Brussel", "NL NATIONAAL"],
  ["Sublime FM", "Sublime FM.png", "http://82.201.47.68:80/SublimeFM2", "Radio Sublime FM", "Sublime FM", "NL NATIONAAL"],
  ["Team FM", "Team FM.png", "http://217.21.199.146:10030/", "Radio Team FM", "Team FM", "NL REGIONAAL"],
  ["Twente FM", "Twente FM.png", "http://217.172.190.185:8068/;stream.mp3", "Radio Twente FM", "Twente FM", "NL REGIONAAL"],
  ["Urk FM Geestelijk", "Urk FM Geestelijk.png", "http://www.urk.fm:8000/geestelijk.mp3", "Radio Urk FM Geestelijk", "Urk FM Geestelijk", "NL REGIONAAL"],
  ["Urk FM", "Urk FM.png", "http://www.urk.fm:8000/urkfm.mp3", "Radio Urk FM", "Urk FM", "NL REGIONAAL"],
  ["ValleiRadio", "ValleiRadio.png", "http://server-25.stream-server.nl:8366/", "Radio ValleiRadio", "ValleiRadio", "NL REGIONAAL"],
  ["Veluwe FM", "Veluwe FM.png", "http://212.45.53.237:8000", "Radio Veluwe FM", "Veluwe FM", "NL REGIONAAL"],
  ["Veronica FM", "Veronica FM.png", "http://8503.live.streamtheworld.com:443/VERONICA_SC", "Radio Veronica FM", "Veronica FM", "NL NATIONAAL"],
  ["Waterstad FM", "Waterstad FM.png", "http://178.19.127.7:80", "Radio Waterstad FM", "Waterstad FM", "NL REGIONAAL"],
  ["Way FM", "Way FM.png", "http://stream.caiw.nl:8000/wayfm", "Radio Way FM", "Way FM", "NL REGIONAAL"],
  ["Weert FM", "Weert FM.png", "http://weertfm.mooo.com:9000/wfm3", "Weert FM", "Weert FM", "NL REGIONAAL"],
  ["Wild FM", "Wild FM.png", "http://icecast.databoss.nl:8000/wildfm.mp3", "Radio Wild FM", "Wild FM", "NL REGIONAAL"],
  ["Zaanradio", "Zaanradio.png", "http://stream.zaanradio.nl:8000/zaanradio", "Zaanradio", "Zaanradio", "NL REGIONAAL"],
] 

TEMP = [
  ["PAC Arizona", "PAC Arizona.png", "http://xrxs.net/video/live-p12ariz-2328.m3u8", "PAC Arizona", "PAC Arizona", "Sport TV"],
  ["PAC Bay Area", "PAC Bay Area.png", "http://xrxs.net/video/live-p12baya-4728.m3u8", "PAC Bay Area", "PAC Bay Area", "Sport TV"],
  ["PAC Los Angeles", "PAC Los Angeles.png", "http://xrxs.net/video/live-p12losa-2328.m3u8", "PAC Los Angeles", "PAC Los Angeles", "Sport TV"],
  ["PAC Mountain", "PAC Mountain.png", "http://xrxs.net/video/live-p12moun-4728.m3u8", "PAC Mountain", "PAC Mountain", "Sport TV"],
  ["PAC National", "PAC National.png", "http://xrxs.net/video/live-p12netw-2328.m3u8", "PAC National", "PAC National", "Sport TV"],
  ["PAC Oregon", "PAC Oregon.png", "http://xrxs.net/video/live-p12oreg-2328.m3u8", "PAC Oregon", "PAC Oregon", "Sport TV"],
  ["PAC Washington", "PAC Washington.png", "http://xrxs.net/video/live-p12wash-2328.m3u8", "PAC Washington", "PAC Washington", "Sport TV"],
  ["Radio 80 TV", "Radio 80.png", "http://sjc-ucdn01-ntt-tcdn.ustream.tv/ams-uhs01/streams/httpflv/ustreamVideo/16115481/streams/live_1_1429087568_2143330791.flv", "Radio 80 TV", "Radio 80 TV", "Sport TV"],
  ["Radio Ideaal TV", "Radio Ideaal.png", "PlayMedia(plugin://plugin.video.youtube/play/?video_id=oBUOFuYktuY)", "Radio Ideaal TV", "Radio Ideaal TV", "RadioTV"],
  ["Sky Sports 1", "Sky Sports 1.png", "rtmp://195.154.168.217:80/liverepeater playpath=303035 swfUrl=http://cdn.goodcast.co/players.swf live=1 pageUrl=http://goodcast.co/.coms token=Fo5_n0w?U.rA6l3-70w47ch", "Sky Sports 1", "Sky Sports 1", "Sport TV"],
  ["Sky Sports 2", "Sky Sports 2.png", "rtmp://195.154.168.217:80/liverepeater playpath=303018 swfUrl=http://cdn.goodcast.co/players.swf live=1 pageUrl=http://goodcast.co/.coms token=Fo5_n0w?U.rA6l3-70w47ch", "Sky Sports 2", "Sky Sports 2", "Sport TV"],
  ["Sky Sports 3", "Sky Sports 3.png", "rtmp://195.154.168.217:80/liverepeater playpath=303019 swfUrl=http://cdn.goodcast.co/players.swf live=1 pageUrl=http://goodcast.co/.coms token=Fo5_n0w?U.rA6l3-70w47ch", "Sky Sports 3", "Sky Sports 3", "Sport TV"],
  ["Sky Sports 4", "Sky Sports 4.png", "rtmp://195.154.168.217:80/liverepeater playpath=303020 swfUrl=http://cdn.goodcast.co/players.swf live=1 pageUrl=http://goodcast.co/.coms token=Fo5_n0w?U.rA6l3-70w47ch", "Sky Sports 4", "Sky Sports 4", "Sport TV"],
  ["Sky Sports 5", "Sky Sports 5.png", "rtmp://195.154.168.217:80/liverepeater playpath=303021 swfUrl=http://cdn.goodcast.co/players.swf live=1 pageUrl=http://goodcast.co/.coms token=Fo5_n0w?U.rA6l3-70w47ch", "Sky Sports 5", "Sky Sports 5", "Sport TV"],
  ["Sky Sports F1", "Sky Sports F1.png", "rtmp://freeview.fms.visionip.tv/live/sports_tonight-sports_tonight-live-25f-16x9-HD", "Sky Sports F1", "Sky Sports F1", "Sport TV"],
  ["Sports Tonight Live", "Sports Tonight Live.png", "http://nlds187.cdnak.neulion.com/nlds/sportsnetnow/sn_360/as/live/sn_360_hd_ipad.m3u8", "Sports Tonight Live", "Sports Tonight Live", "Sport TV"],
  ["Sportsnet 360", "Sportsnet 360.png", "http://nlds187.cdnak.neulion.com/nlds/sportsnetnow/sn_360/as/live/sn_360_hd_ipad.m3u8", "Sportsnet 360", "Sportsnet 360", "Sport TV"],
  ["Skyline FM TV", "Skyline FM.png", "http://www.skylinertv.nl/inc/tv_stream.php", "Radio Skyline FM TV", "Radio Skyline FM TV", "Skyline FM TV"],
]

###
def index():
    if settings.getSetting( "HalowTV" )=='true':
        for channel in SATCHANNELS:
            if settings.getSetting( channel[0] )=='true' and settings.getSetting( "GEOIP" )=='false':
                addLink(channel[0],channel[2], "playVideo", os.path.join(IMG_DIR, channel[1]), channel[3])
    for channel in TV24M3U:
        if settings.getSetting( channel[0] )=='true' and settings.getSetting( "GEOIP" )=='false':
            addLink(channel[0],channel[2], "playVideo", os.path.join(IMG_DIR, channel[1]), channel[3])
        else:
            #print ""
            xbmc.log("plugin.video.nederland24:: %s not set (GEOIP)" % str(channel[0]))
    if int(settings.getSetting ( "Depth_Acht" ))!=0:
        url='http://feeds.nos.nl/journaal20uur'
        depth=int(settings.getSetting ( "Depth_Acht" ))
        additionalChannels(url, depth)
    if int(settings.getSetting ( "Depth_Jeugd" ))!=0:
        url='http://feeds.nos.nl/vodcast_jeugdjournaal'
        depth=int(settings.getSetting ( "Depth_Jeugd" ))
        additionalChannels(url, depth)
    for channel in TVM3U:
        if settings.getSetting( channel[0] )=='true' and settings.getSetting( "GEOIP" )=='false':
            addLink(channel[0],channel[2], "playVideo", os.path.join(IMG_DIR, channel[1]), channel[3])
        else:
            #print ""
            xbmc.log("plugin.video.nederland24:: %s not set (GEOIP)" % str(channel[0]))
    for channel in RADIOM3U:
        if settings.getSetting( channel[0] )=='true' and settings.getSetting( "GEOIP" )=='false':
            addLink(channel[0],channel[2], "playMusic", os.path.join(IMG_DIR, channel[1]), channel[3])
        else:
            #print ""
            xbmc.log("plugin.video.nederland24:: %s not set (GEOIP)" % str(channel[0]))		
    else:
        #print ""
        xbmc.log("plugin.video.nederland24:: No additional channels set")
    xbmcplugin.endOfDirectory(pluginhandle)

def resolve_http_redirect(url, depth=0):
    if depth > 10:
        raise Exception("Redirected "+depth+" times, giving up.")
    o = urlparse.urlparse(url,allow_fragments=True)
    conn = httplib.HTTPConnection(o.netloc)
    path = o.path
    if o.query:
        path +='?'+o.query
    conn.request("HEAD", path)
    res = conn.getresponse()
    headers = dict(res.getheaders())
    if headers.has_key('location') and headers['location'] != url:
        return resolve_http_redirect(headers['location'], depth+1)
    else:
        return url

def extract_url(chan):
    URL=API_URL+BASE_URL+(chan)
    req = urllib2.Request(URL)
    req.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(req)
    page = response.read()
    response.close()
    videopre=re.search(r'http:(.*?)url',page).group()
    prostream= (videopre.replace('\/', '/'))
    video = resolve_http_redirect(prostream, 3)
    return video

def update():
    if m3uLocation == "":
        addon.openSettings()
    tempM3u = "#EXTM3U\n\n"
    if settings.getSetting( "HalowTV" )=='true':				
        for channel in SATCHANNELS:
            tempM3u += "#EXTINF:-1 tvg-id=\""+channel[4]+"\" tvg-name=\""+channel[0]+"\" tvg-logo=\""+channel[1]+"\" group-title=\""+channel[5]+"\", "+channel[0]+"\n"
            finalUrl = channel[2]
            tempM3u += str(finalUrl)+"\n\n"
    for channel in TV24M3U:
        tempM3u += "#EXTINF:-1 tvg-id=\""+channel[4]+"\" tvg-name=\""+channel[0]+"\" tvg-logo=\""+channel[1]+"\" group-title=\""+channel[5]+"\", "+channel[0]+"\n"
        URL=API_URL+BASE_URL+channel[2]+"&token=%s" % collect_token()
        req = urllib2.Request(URL)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Referer', REF_URL)
        response = urllib2.urlopen(req)
        page = response.read()
        response.close()
        videopre=re.search(r'http:(.*?)url',page).group()
        prostream= (videopre.replace('\/', '/'))
        finalUrl = resolve_http_redirect(prostream)
        tempM3u += str(finalUrl)+"\n\n"
    for channel in TVM3U:
        tempM3u += "#EXTINF:-1 tvg-id=\""+channel[4]+"\" tvg-name=\""+channel[0]+"\" tvg-logo=\""+channel[1]+"\" group-title=\""+channel[5]+"\", "+channel[0]+"\n"
        finalUrl = channel[2]
        tempM3u += str(finalUrl)+"\n\n"
    for channel in RADIOM3U:
        tempM3u += "#EXTINF:-1 tvg-id=\""+channel[4]+"\" tvg-name=\""+channel[0]+"\" tvg-logo=\""+channel[1]+"\" group-title=\""+channel[5]+"\" radio=\"true\", "+channel[0]+"\n"
        finalUrl = channel[2]
        tempM3u += str(finalUrl)+"\n\n"
    write(tempM3u, m3u_file)
    xbmc.executebuiltin("StartPVRManager")
    time.sleep(2)
    xbmc.executebuiltin("Notification("+localtxt204+","+localtxt313+", 5000, %s)" % (skinimage))

def favour():
    if favLocation == "":
        addon.openSettings()
    tempFav = "<favourites>\n"
    if settings.getSetting( "HalowTV" )=='true':		
        for channel in SATCHANNELS:
            tempFav += "	<favourite name=\""+channel[0]+"\" thumb=\"special://home/addons/plugin.program.openeleq.tools/resources/media/"+channel[1]+"\">PlayMedia(&quot;"
            finalUrl = channel[2]
            tempFav += str(finalUrl)+"&quot;)</favourite>\n"
    for channel in TV24M3U:
        tempFav += "	<favourite name=\""+channel[0]+"\" thumb=\"special://home/addons/plugin.program.openeleq.tools/resources/media/"+channel[1]+"\">PlayMedia(&quot;"
        URL=API_URL+BASE_URL+channel[2]+"&token=%s" % collect_token()
        req = urllib2.Request(URL)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Referer', REF_URL)
        response = urllib2.urlopen(req)
        page = response.read()
        response.close()
        videopre=re.search(r'http:(.*?)url',page).group()
        prostream= (videopre.replace('\/', '/'))
        finalUrl = resolve_http_redirect(prostream)
        tempFav += str(finalUrl)+"&quot;)</favourite>\n"
    for channel in TVM3U:
        tempFav += "	<favourite name=\""+channel[0]+"\" thumb=\"special://home/addons/plugin.program.openeleq.tools/resources/media/"+channel[1]+"\">PlayMedia(&quot;"
        finalUrl = channel[2]
        tempFav += str(finalUrl)+"&quot;)</favourite>\n"
    for channel in RADIOM3U:
        tempFav += "	<favourite name=\""+channel[0]+"\" thumb=\"special://home/addons/plugin.program.openeleq.tools/resources/media/"+channel[1]+"\">PlayMedia(&quot;"
        finalUrl = channel[2]
        tempFav += str(finalUrl)+"&quot;)</favourite>\n"
    tempFav += "</favourites>"
    write(tempFav, fav_file)
    xbmc.executebuiltin("Notification("+localtxt209+","+localtxt313+", 5000, %s)" % (skinimage))

def test():
    preurl = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=tt'
    url = preurl+'4122068'
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    soup = BeautifulSoup(link, 'html.parser')
	
def testbackup2(imdb_id):
    preurl = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=tt'
    url = preurl+imdb_id
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    match = re.compile('<id>.+?<',re.DOTALL).findall(link)
    temp = str(match)
    tvdb_id = temp[6:-3]

def testbackup():
    url = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=tt4122068'
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    longtvdb_id = re.search(r'>.*?<', shortsource).group(0)
    tvdb_id = longtvdb_id[1:-1]
    write(tvdb_id, fav_file)

def BVLSSched():
    link = Get_url()
    match=re.compile('>.+?<',re.DOTALL).findall(link)
    for id in match:
        name = timestr + " == " + name + " (" + stream + ")"
        addLink(name,'url','mode',icon,fanart)
	
def Get_url():
    url = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=tt4122068'
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link 

def write(what, filelocation):
    fopen = open(filelocation, "w")
    fopen.write(what)
    fopen.close()

def collect_token():
    req = urllib2.Request(TOKEN_URL)
    req.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(req)
    page = response.read()
    response.close()
    token = re.search(r'npoplayer.token = "(.*?)"',page).group(1)
    #xbmc.log("plugin.video.nederland24:: oldtoken: %s" % token)
    # site change, token invalid, needs to be reordered. Thanks to rieter for figuring this out very quickly.
    first = -1
    last = -1
    for i in range(5, len(token) - 5, 1):
	#xbmc.log("plugin.video.nederland24:: %s" % token[i])
        if token[i].isdigit():
            if first < 0:
                first = i
                #xbmc.log("plugin.video.nederland24:: %s" % token[i])
            elif last < 0:
                last = i
                #xbmc.log("plugin.video.nederland24:: %s" % token[i])
                break

    newtoken = list(token)
    if first < 0 or last < 0:
        first = 12
        last = 13
    newtoken[first] = token[last]
    newtoken[last] = token[first]
    newtoken = ''.join(newtoken)
    #xbmc.log("plugin.video.nederland24:: newtoken: %s" % newtoken)
    return newtoken

def addLink(name, url, mode, iconimage, description):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name,
    	                                  "Plot":description,
    	                                  "TVShowTitle":name,
    	                                  "Playcount": 0,
    	                                  })
    
    liz.setProperty("fanart_image", os.path.join(IMG_DIR, "fanart.png"))
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def additionalChannels(url, depth):
    i = 0
    #depth = depth
    URL = url
    #URL = 'http://feeds.nos.nl/journaal'
    items = SoupStrainer('item')
    for tag in BeautifulStoneSoup(urllib2.urlopen(URL).read(), parseOnlyThese=items):
        title = tag.title.contents[0]
        url = tag.guid.contents[0]
        img = os.path.join(IMG_DIR, "placeholder24.png")
        addLink(title, url, "playVideo", img, '')
        i += 1
        if i == int(depth):
            break

def playVideo(url):
    media = url
    finalUrl=""
    if media and media.startswith("http://"):
        finalUrl=media
    else:
        URL=API_URL+BASE_URL+media+"&token=%s" % collect_token()
        req = urllib2.Request(URL)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Referer', REF_URL)
        response = urllib2.urlopen(req)
        page = response.read()
        response.close()
        videopre=re.search(r'http:(.*?)url',page).group()
        prostream= (videopre.replace('\/', '/'))
        finalUrl = resolve_http_redirect(prostream)
    if finalUrl:
        listitem = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def playMusic(url):
    media = url
    finalUrl=""
    if media and media.startswith("http://"):
        finalUrl=media
    else:
        URL=API_URL+BASE_URL+media+"&token=%s" % collect_token()
        req = urllib2.Request(URL)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Referer', REF_URL)
        response = urllib2.urlopen(req)
        page = response.read()
        response.close()
        videopre=re.search(r'http:(.*?)url',page).group()
        prostream= (videopre.replace('\/', '/'))
        finalUrl = resolve_http_redirect(prostream)
    if finalUrl:
        listitem = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))


if mode == "playVideo":
    playVideo(url)
if mode == "playMusic":
    playMusic(url)
elif mode == "update":
    update()
elif mode == "favour":
    favour()
elif mode == "test":
    test()
else:
    index()

