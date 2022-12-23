#  Drakkar-Software OctoBot-Backtesting
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
# from distutils.extension import Extension
import os

from setuptools import dist
dist.Distribution().fetch_build_eggs(['Cython>=0.29.32'])

try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
except ImportError:
    # create closure for deferred import
    def cythonize(*args, **kwargs):
        from Cython.Build import cythonize
        return cythonize(*args, **kwargs)

    def build_ext(*args, **kwargs):
        from Cython.Distutils import build_ext
        return build_ext(*args, **kwargs)

from setuptools import find_packages
from setuptools import setup, Extension

from octobot_backtesting import PROJECT_NAME, VERSION

PACKAGES = find_packages(exclude=["tests"])

packages_list = [
    "octobot_backtesting.channels_manager",
    "octobot_backtesting.backtest_data",
    "octobot_backtesting.backtesting",
    "octobot_backtesting.importers.data_importer",
    "octobot_backtesting.importers.exchanges.util",
    "octobot_backtesting.importers.exchanges.exchange_importer",
    "octobot_backtesting.importers.social.social_importer",
    "octobot_backtesting.data.data_file_manager",
    "octobot_backtesting.util.backtesting_util",
    "octobot_backtesting.collectors.data_collector",
    "octobot_backtesting.collectors.exchanges.exchange_collector",
    "octobot_backtesting.collectors.exchanges.abstract_exchange_bot_snapshot_collector",
    "octobot_backtesting.collectors.exchanges.abstract_exchange_history_collector",
    "octobot_backtesting.collectors.exchanges.abstract_exchange_live_collector",
    "octobot_backtesting.collectors.social.social_collector",
    "octobot_backtesting.converters.data_converter",
    "octobot_backtesting.time.time_manager",
    "octobot_backtesting.time.channel.time",
    "octobot_backtesting.time.channel.time_updater",
]

ext_modules = [
    Extension(package, [f"{package.replace('.', '/')}.py"])
    for package in packages_list]

# long description from README file
# with open('README.md', encoding='utf-8') as f:
#     DESCRIPTION = f.read()

REQUIRED = open('requirements.txt').readlines()
REQUIRES_PYTHON = '>=3.8'
CYTHON_DEBUG = False if not os.getenv('CYTHON_DEBUG') else os.getenv('CYTHON_DEBUG')

setup(
    name=PROJECT_NAME,
    version=VERSION,
    url='https://github.com/Drakkar-Software/OctoBot-Backtesting',
    license='LGPL-3.0',
    author='Drakkar-Software',
    author_email='drakkar-software@protonmail.com',
    description='OctoBot project backtesting engine',
    packages=PACKAGES,
    include_package_data=True,
    # long_description=DESCRIPTION,
    cmdclass={'build_ext': build_ext},
    tests_require=["pytest"],
    test_suite="tests",
    zip_safe=False,
    data_files=[],
    setup_requires=REQUIRED if not CYTHON_DEBUG else [],
    install_requires=REQUIRED,
    ext_modules=cythonize(ext_modules, gdb_debug=CYTHON_DEBUG),
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Cython',
    ],
)
