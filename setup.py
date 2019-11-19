from setuptools import setup

setup(
      name='mangodb',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/vharitonsky/mangodb',
      author='Vitaliy Kharitonskiy',
      author_email='vharitonsky@gmail.com',
      license='MIT',
      packages=['mangodb'],
      zip_safe=False,
      install_requires=[
            'pymongo',
            'motor',
      ],
)
