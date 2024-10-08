from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cbpi4-PCF8575-GPIO',
      version='0.0.10',
      description='CraftBeerPi4 PCF8575 Actor Plugin',
      author='Michael Giesbrecht',
      author_email='michael_giesbrecht"outlook.com',
      url='https://github.com/MichaelGiesbrecht/cbpi4-PCF8575-GPIO',
      include_package_data=True,
      keywords='globalsettings',
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-PCF8575-GPIO': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-PCF8575-GPIO'],
      install_requires=['smbus2','cbpi4>=4.1.10.rc2','pcf8575'],
      long_description=long_description,
      long_description_content_type='text/markdown'
     )
