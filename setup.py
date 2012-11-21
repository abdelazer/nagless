from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='nagless',
      version=version,
      description="Nagless helps you interact better with colleagues by managing the timing of reminders and check-ins",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Keith Fahlgren',
      author_email='abdelazer+nagless@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      dependency_links = [
      ],

      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'psycopg2', # locally
          'uwsgi',

          'Django>=1.4',
          'fabric>=1.5',
          'django-social-auth',
          'south',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
