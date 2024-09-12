import io
#import re
from setuptools import setup

import os
import shutil
try:
    os.remove(os.path.join('pydebugger', '__version__.py'))
except:
    pass
shutil.copy2('__version__.py', 'pydebugger')

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

# with io.open("__version__.py", "rt", encoding="utf8") as f:
    # version = re.search(r"version = \'(.*?)\'", f.read()).group(1)
from pydebugger import __version__
version = __version__

setup(
    name="pydebugger",
    version=version,
    url="https://github.com/cumulus13/pydebugger",
    project_urls={
        "Documentation": "https://github.com/cumulus13/pydebugger",
        "Code": "https://github.com/cumulus13/pydebugger",
    },
    license="BSD",
    author="Hadi Cahyadi LD",
    author_email="cumulus13@gmail.com",
    maintainer="cumulus13 Team",
    maintainer_email="cumulus13@gmail.com",
    description="Print objects with inspection details and color.",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=["pydebugger"],
    data_files=['__version__.py', 'README.md', 'LICENSE.md'],
    package_data = {
       '': ['*.txt', '*.ini', '*.rst', '*.py'] 
    },     
    install_requires=[
        'make_colors>=3.12',
        'configset',
        'cmdw',
        'configparser',
        'sqlalchemy',
        'rich'
    ],
    entry_points = {
         "console_scripts": [
             "pydebugger = pydebugger.debug:usage",
         ]
    },
    include_package_data=True,
    python_requires=">=2.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
