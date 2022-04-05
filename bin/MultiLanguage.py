#!/usr/bin/python
# ----------------------------------------------------------------------------
# MultiLanguage: Get the multi-language strings for console.
#
# Author: Bin Zhang
#
# License: MIT
# ----------------------------------------------------------------------------
'''
Get the multi-language strings for console.
'''

import cocos
import os
import sys
import json
import locale

def get_current_path():
    if getattr(sys, 'frozen', None):
        ret = os.path.realpath(os.path.dirname(sys.executable))
    else:
        ret = os.path.realpath(os.path.dirname(__file__))

    return ret

class MultiLanguage:
    CONFIG_FILE_NAME = 'strings.json'
    DEFAULT_LANGUAGE = 'en'
    instance = None

    @classmethod
    def get_available_langs(cls):
        info = cls.get_instance().cfg_info
        ret = []
        if info is not None:
            for key in list(info.keys()):
                if isinstance(key, str):
                    ret.append(key)

        return ret

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = MultiLanguage()

        return cls.instance

    @classmethod
    def get_string(cls, key, fmt_value=None):
        fmt = cls.get_instance().get_current_string(key)
        if fmt_value is None:
            ret = fmt
        else:
            if isinstance(fmt_value, tuple):
                dst_values = []
                for value in fmt_value:
                    if isinstance(value, str):
                        dst_values.append(value.encode(cls.get_instance().get_encoding()))
                    else:
                        dst_values.append(value)
                ret = fmt % tuple(dst_values)
            elif isinstance(fmt_value, str):
                ret = fmt % fmt_value.encode(cls.get_instance().get_encoding())
            else:
                ret = fmt % fmt_value

        return ret


    @classmethod
    def set_language(cls, lang):
        cls.get_instance().set_current_language(lang)

    def __init__(self):
        cfg_file_path = os.path.join(get_current_path(), MultiLanguage.CONFIG_FILE_NAME)

        try:
            sys_lang, self.encoding = locale.getdefaultlocale()
        except:
            sys_lang = None
            self.encoding = None
            pass

        if self.encoding is None:
            self.encoding = 'utf-8'

        if sys_lang is None:
            cur_lang_key = MultiLanguage.DEFAULT_LANGUAGE
        else:
            cur_lang_key = self.get_lang_key(sys_lang)

        # get the strings info
        if os.path.isfile(cfg_file_path):
            f = open(cfg_file_path)
            self.cfg_info = json.load(f)
            f.close()

            self.cur_lang_strings = self.cfg_info.get(cur_lang_key)

            self.default_lang_strings = self.cfg_info.get(MultiLanguage.DEFAULT_LANGUAGE)
        else:
            self.cfg_info = None
            self.cur_lang_strings = None
            self.default_lang_strings = None

    def get_lang_key(self, sys_lang):
        sys_lang_info = sys_lang.split('_')
        lang = sys_lang_info[0]
        lang = lang.lower()
        region = None
        if len(sys_lang_info) > 1:
            region = sys_lang_info[1]
            region = region.lower()

        if lang == 'zh':
            if (region is None) or (region == 'cn'):
                ret = lang
            else:
                ret = 'zh_tw'
        else:
            ret = lang

        return ret

    def has_key(self, key, strings_info):
        ret = False
        if strings_info is not None and strings_info.get(key):
            ret = True

        return ret

    def set_current_language(self, lang):
        if (self.cfg_info is not None) and (self.cfg_info.get(lang)):
            self.cur_lang_strings = self.cfg_info[lang]
        else:
            cocos.Logging.warning(MultiLanguage.get_string('COCOS_WARNING_LANG_NOT_SUPPORT_FMT', lang))

    def get_encoding(self):
        return self.encoding

    def get_current_string(self, key):
        if self.has_key(key, self.cur_lang_strings):
            ret = self.cur_lang_strings[key]
        elif self.has_key(key, self.default_lang_strings):
            ret = self.default_lang_strings[key]
        else:
            ret = key
        return ret
