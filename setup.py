import io
import os

from setuptools import find_packages, setup

NAME = 'pymv'

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name=NAME,
    version='1.4',
    description='CLI wrapper of rope\'s module moving functionality',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ridecell & contributors',
    author_email='john@johngm.com',
    python_requires='>=3.7.0',
    url='https://github.com/Ridecell/pymv',
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    entry_points={
        'console_scripts': ['pymv=pymv.main:main'],
    },
    install_requires=[
        # 'git+https://github.com/Ridecell/rope'
    ],
    extras_require={},
    include_package_data=True,
    license='MIT',
)
