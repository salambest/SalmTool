[app]

# ---------------------------------------------------------------------------
# App identity
# ---------------------------------------------------------------------------
title = SalmTool Ultimate
package.name = salmtoolultimate
package.domain = org.salmtool

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,md
version = 1.0.0

# ---------------------------------------------------------------------------
# Python / Kivy requirements bundled into the APK.
#
# python3 AND hostpython3 are BOTH pinned to 3.11.15, and MUST match
# exactly - python-for-android hard-fails with:
#   "Build failed: python3 should have same version as hostpython3, X != Y"
# if they differ, because hostpython3 (the build-time interpreter used to
# cross-compile/install packages) is resolved as an independent recipe and
# does not automatically inherit the version pinned on python3. This exact
# python3==X,hostpython3==X syntax is documented officially at:
# https://python-for-android.readthedocs.io/en/latest/buildoptions.html
#
# 3.11.15 is used (not 3.13/3.14) because newer CPython ships a remote
# debugging module (Python/remote_debug.h, Python/remote_debugging.c) that
# calls preadv()/pwritev() unconditionally. Those functions are only
# declared in the Android NDK headers for API level 24+, so building
# against android.minapi = 23 fails with:
#   "implicit declaration of function 'preadv'"
# The 3.11 series predates that module entirely.
#
# pyaxmlparser is intentionally left out: it needs an lxml recipe that
# isn't available on every python-for-android setup. The apk_analyzer
# module already falls back to a built-in heuristic parser when
# pyaxmlparser is missing, so the app stays fully functional either way.
# ---------------------------------------------------------------------------
requirements = python3==3.11.15,hostpython3==3.11.15,kivy==2.3.0,kivymd==1.2.0,pillow,requests,plyer,fpdf2

icon.filename = %(source.dir)s/icon.png

orientation = portrait
fullscreen = 0

# ---------------------------------------------------------------------------
# Android permissions required by the feature modules:
#   INTERNET / ACCESS_NETWORK_STATE  -> Network Analyzer, AI Helper
#   ACCESS_WIFI_STATE                -> WiFi Analyzer
#   READ/WRITE_EXTERNAL_STORAGE      -> APK Analyzer, EXIF Analyzer,
#                                       File Manager, Report Generator
# ---------------------------------------------------------------------------
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 23
android.ndk_api = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

# ---------------------------------------------------------------------------
# python-for-android is pinned to the latest stable, officially tagged
# GitHub release (v2026.05.09) instead of the `master` branch. Verified
# directly against https://github.com/kivy/python-for-android/releases -
# the real tag includes the "v" prefix and zero-padded month/day
# (v2026.05.09, NOT 2026.5.9). `master` is a moving target - it is what
# silently changed the default python3/hostpython3 version to 3.14.2
# between two earlier build attempts. Pinning a released tag makes the
# build reproducible.
# ---------------------------------------------------------------------------
p4a.branch = v2026.05.09

[buildozer]
log_level = 2
warn_on_root = 1
