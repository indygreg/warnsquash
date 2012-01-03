from distutils.core import setup

setup(
    name='WarnSquash',
    version='0.0.1',
    author='Gregory Szorc',
    author_email='gregory.szorc@gmail.com',
    packages=['warnsquash'],
    scripts=['bin/warnsquash'],
    license='LICENSE.txt',
    description='Tool to help squash compiler warnings.',
    long_description=open('README.rst').read(),
)
