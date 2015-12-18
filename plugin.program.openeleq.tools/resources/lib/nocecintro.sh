#!/bin/sh

cp /storage/.kodi/addons/skin.aeon.nox.silvo/1080i/DialogKaiToast.visible.xml /storage/.kodi/addons/skin.aeon.nox.silvo/1080i/DialogKaiToast.xml
cp /storage/.kodi/addons/skin.aeon.nox.silvo/1080i/Pointer.visible.xml /storage/.kodi/addons/skin.aeon.nox.silvo/1080i/Pointer.xml
sleep 7
kodi-send -a "ReloadSkin()"