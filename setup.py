from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
      name='mangodb',
      long_description=long_description,
      long_description_content_type='text/markdown',
      version='0.8',
      description='Temporary database driver',
      url='http://github.com/vharitonsky/mangodb',
      author='Vitaliy Kharitonskiy',
      author_email='vharitonsky@gmail.com',
      license='MIT',
      packages=find_packages(exclude=["tests"]),
      zip_safe=False,
      install_requires=[
            'pymongo>=2.9.5',
            'motor==2.0.0',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
)
