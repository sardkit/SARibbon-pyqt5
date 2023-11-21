from setuptools import setup, find_packages

setup(
    name='PySARibbon',
    version='1.0.2',
    description='4种目前常见的ribbon样式.',
    # long_description=read('README.md'),
    keywords=('python', 'ribbon'),
    license='GPL',

    url='https://github.com/sardkit/pysaribbon',
    author='sardkit',
    author_email='sardkit@163.com',

    packages=find_packages(),
    py_modules=[],
    install_requires=[
        'pyqt5',
    ],

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',

        'Programming Language :: Python :: 3',
    ],

    scripts=[]
)
