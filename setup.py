from setuptools import setup

setup(
    name='FlaskSQLA-ApiCrud',
    version='0.1',
    url='https://github.com/Sarodus/FlaskSQLA_API_CRUD',
    license='BSD',
    author='Jordi Avella',
    description='API CRUD for Flask-SQLAlchemy',
    packages=['flasksqla_apicrud'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask-SQLAlchemy>=2.2'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)