"""Setup script for the Filer project.
"""
import setuptools


PACKAGES = [
    'logga==1.0.0',
    'pytest==2.9.2',
    'pytest-cov==2.3.0',
    'factory-boy==2.8.1',
    'pylint==1.6.4',
    'sphinx_rtd_theme==0.1.10a0',
    'Sphinx==1.4.5',
]

SETUP_KWARGS = {
    'name': 'filer',
    'version': '1.0.0',
    'description': 'Common file-based utilities',
    'author': 'Lou Markovski',
    'author_email': 'lou.markovski@gmail.com',
    'url': 'https://github.com/loum/filer',
    'install_requires': PACKAGES,
    'packages': setuptools.find_packages(),
    'package_data': {
        'filer': [
        ],
    },
}

setuptools.setup(**SETUP_KWARGS)
