from setuptools import setup, find_packages

setup(
      name='mangodb',
      version='0.2',
      description='Temporary database driver',
      url='http://github.com/vharitonsky/mangodb',
      author='Vitaliy Kharitonskiy',
      author_email='vharitonsky@gmail.com',
      license='MIT',
      packages=find_packages(exclude=["tests"]),
      zip_safe=False,
      install_requires=[
            'pymongo==3.9.0',
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
