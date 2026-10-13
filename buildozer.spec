[app]
title = WiFi Audit
package.name = wifiaudit
package.domain = org.osdbayu457

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
source.include_patterns = data/*.txt

version = 1.0
requirements = python3,kivy==2.2.1

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,ACCESS_NETWORK_STATE

android.api = 31
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
