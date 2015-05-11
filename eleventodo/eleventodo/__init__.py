from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    session_factory = UnencryptedCookieSessionFactoryConfig('secret_key')
    config = Configurator(settings=settings,
                          session_factory=session_factory,
                         )
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static', 'deform:static')
    config.add_route('list', '/')
    config.add_route('add', '/add')
    config.add_route('edit_todo_item', '/edit/{id}')
    config.add_route('delete', '/delete/{id}')
    config.add_route('tags', '/tags')
    config.add_route('tag', '/tags/{tag_name}')
    config.scan()
    return config.make_wsgi_app()
