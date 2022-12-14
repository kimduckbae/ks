import requests
from os import getenv
from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request
)
from configs.derived_vars import is_development
from .search import search

pages = Blueprint('pages', __name__)


@pages.get('/')
def get_home():
    props = {}
    base = request.args.to_dict()
    base.pop('o', None)
    response = make_response(render_template(
        'home.html',
        props=props,
        base=base
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@pages.get('/antiscraper')
def do_antiscraper_thing():
    """
    Pass the url param to the proxy server.
    """
    params = request.args.to_dict()
    url = params['antiscraper-url']
    try:
        res = requests.get(
            url,
            proxies={
                'http': getenv('ANTIANTISCRAPER_PROXY'),
                'https': getenv('ANTIANTISCRAPER_PROXY')
            } if getenv('ANTIANTISCRAPER_PROXY') else None,
            headers={
                'referer': "https://www.patreon.com"
            },
        )
        res.raise_for_status()
        return redirect(res.url)
    except requests.HTTPError as error:
        current_app.logger.exception(f'Couldn\'t bypass "{url}". Reason: {error}')
    except Exception as error:
        current_app.logger.exception(f'Couldn\'t bypass "{url}". Reason: {error}')
        return ('Error while trying to bypass the antiscraper link. The admins were notified of the problem.', 500)


@pages.route('/help/bans')
def bans():
    props = dict(
        currentPage='help'
    )
    response = make_response(render_template(
        'help/bans.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


if is_development:
    from .development import development
    pages.register_blueprint(development)

pages.register_blueprint(search)
