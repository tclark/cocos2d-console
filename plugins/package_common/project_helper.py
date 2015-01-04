
import sys
import getopt
import ConfigParser
import json
import shutil
import cocos
import cocos_project
import urllib2
import re
import hashlib
from pprint import pprint
from collections import OrderedDict
from time import time
from package_common import *
from package_helper import PackageHelper
from install_helper import InstallHelper

class ProjectHelper:

    SUPPORTED_PLATFORMS = ("proj.android", "proj.ios_mac", "proj.win32")
    PACKAGES_DIRNAME = "packages"

    @classmethod
    def get_current_project(cls):
        cwd = os.path.realpath(os.getcwd())
        prefix = cwd

        project = {}
        project["path"] = prefix

        project["classes_dir"] = "Classes"
        if os.path.exists(prefix + os.sep + project["classes_dir"]):
            project["type"] = "cpp"
        else:
            prefix = "frameworks" + os.sep + "runtime-src"
            project["classes_dir"] = prefix + os.sep + "Classes"
            if os.path.exists(cwd + os.sep + project["classes_dir"]):
                project["type"] = "script"

        if not "type" in project:
            message = "Fatal: you must run `cocos add-framework` at project root dir"
            raise cocos.CCPluginError(message)

        for platform in cls.SUPPORTED_PLATFORMS:
            path = project["path"] + os.sep + prefix + os.sep + platform
            if os.path.exists(path):
                project[platform] = path

        project["packages_dir"] = project["path"] + os.sep + cls.PACKAGES_DIRNAME
        return project

    @classmethod
    def add_framework(cls, project, package_name):
        package_data = PackageHelper.get_installed_package_data(package_name)
        if package_data is None:
            print "[PACKAGE] not found package '%s'" % package_name
            return

        print "[PROJECT] > project path: %s" % project["path"]
        print "[PROJECT] > project type: %s" % project["type"]
        print "[PROJECT] > Adding '%s %s (%s)' ..." % (package_data["name"], package_data["version"], package_data["author"])

        # unpacking files
        ensure_directory(project["packages_dir"])
        unpacker = ZipUnpacker(PackageHelper.get_installed_package_zip_path(package_data))
        unpacker.unpack(project["packages_dir"])

        # execute install.json
        install_helper = InstallHelper(project, package_data)
        install_helper.run()
