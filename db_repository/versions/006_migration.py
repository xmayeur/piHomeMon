from sqlalchemy import *

pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
             Column('id', Integer, primary_key=True, nullable=False),
             Column('email', String(length=255)),
             Column('password', String(length=255)),
             Column('nickname', String(length=255)),
             Column('active', Boolean),
             Column('confirmed_at', DateTime),
             )


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['nickname'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['nickname'].drop()
