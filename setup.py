from distutils.core import setup

setup(
    name='piHomeMon',
    version='1.0',
    packages=['app', 'app.db_repository', 'app.db_repository.versions', 'db_repository', 'db_repository.versions'],
    url='https://github.com/xmayeur/piHomeMon.git',
    license='',
    author='X. Mayeur',
    author_email='xavier@mayeur.be',
    description='Home device monitoring server',
    requires=['flask', 'flask_security', 'flask_socketio', 'fabric3', 'kodipydent']

)
