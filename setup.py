from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='meetenjoy',
    version='1.0.4',
    description='Tool for conferences',
    license="MIT",
    long_description=long_description,
    author='Vlad Lytvynenko',
    author_email='sir.sagramor@gmail.com',
    url="https://meetenjoy.herokuapp.com",
    download_url="https://github.com/vladlytvynenko/mj/archive/refs/tags/1.0.4.tar.gz",
    packages=['meetenjoy'],
    install_requires=['requests', 'appdirs'],
    scripts=[
        'scripts/mj',
    ]
)
