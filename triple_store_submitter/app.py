import aiohttp
import datetime
import logging
import os
import rdflib
import SPARQLWrapper
import warnings

from aiohttp import web

from triple_store_submitter.consts import BuildInfo, ENV_CONFIG
from triple_store_submitter.config import SubmitterConfigParser, SubmitterConfig


warnings.filterwarnings('ignore')


def validate_token(cfg: SubmitterConfig, request: web.Request):
    if cfg.security.token is None:
        return True
    return request.headers.get('Authorization') == f'Bearer {cfg.security.token}'


async def store_data(cfg: SubmitterConfig, request: web.Request):
    data = await request.content.read()
    g = rdflib.Graph()
    g.parse(data=data, format='turtle')

    triples = [
        f'{s.n3()} {p.n3()} {o.n3()} .' for s, p, o in g
    ]

    sparql = SPARQLWrapper.SPARQLWrapper(cfg.triple_store.sparql_endpoint)
    sparql.setMethod('POST')

    if cfg.triple_store.auth_method:
        sparql.setHTTPAuth(SPARQLWrapper.BASIC)
        sparql.setCredentials(cfg.triple_store.auth_username, cfg.triple_store.auth_password)

    if cfg.triple_store.graph_named is True and cfg.triple_store.graph_type:
        t = rdflib.URIRef(cfg.triple_store.graph_type)
        graph_uri = None
        for s, p, o in g.triples((None, rdflib.RDF.type, t)):
            graph_uri = s.n3()
        if graph_uri is None:
            logging.warning(f'Graph URI not found (type: {t})')
        sparql.setQuery('DROP SILENT GRAPH ' + graph_uri + ';\nCREATE GRAPH ' + graph_uri + ';\nINSERT DATA { GRAPH ' + graph_uri + ' { ' + '\n'.join(triples) + '} };')
    else:
        sparql.setQuery('INSERT DATA { ' + '\n'.join(triples) + '}')
    sparql.setReturnFormat(SPARQLWrapper.JSON)
    sparql.query().convert()


async def update_metadata(cfg: SubmitterConfig):
    headers = dict()
    if cfg.fdp.token is not None:
        headers['Authorization'] = f'Bearer {cfg.fdp.token}'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(cfg.fdp.distribution) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f'Failed to GET distribution (HTTP {resp.status}): {data}')

        g = rdflib.Graph()
        g.parse(data=data, format='turtle')
        timestamp = rdflib.Literal(datetime.datetime.utcnow())
        for s, p, o in g.triples((None, rdflib.RDF.type, rdflib.DCAT.Distribution)):
            g.set((s, rdflib.DCTERMS.modified, timestamp))
        new_data = g.serialize(format='turtle')

        async with session.put(cfg.fdp.distribution, data=new_data, headers={'Content-Type': 'text/turtle'}) as resp:
            data = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f'Failed to PUT distribution (HTTP {resp.status}): {data}')


async def index_handler(request: web.Request):
    return web.json_response(BuildInfo.obj())


async def submit_handler(request: web.Request):
    cfg = request.app['cfg']

    if not validate_token(cfg, request):
        raise web.HTTPUnauthorized(text='Invalid token')
    if request.headers.get('Content-Type').lower() != 'text/turtle':
        raise web.HTTPUnsupportedMediaType(text='Unsupported content type')

    try:
        await store_data(cfg, request)
    except Exception as e:
        msg = f'Failed to store data in triple store: {e}'
        logging.warning(msg)
        return web.HTTPInternalServerError(text=msg)

    if cfg.fdp.distribution is not None:
        try:
            await update_metadata(cfg)
        except Exception as e:
            msg = f'Failed to store metadata in FAIR Data Point: {e}'
            logging.warning(msg)
            return web.HTTPInternalServerError(text=msg)

    return web.HTTPNoContent()


def init_func(argv):
    app = web.Application()

    # load config
    config_file = os.getenv(ENV_CONFIG)
    cfg = SubmitterConfigParser()
    if config_file is not None:
        with open(config_file) as f:
            app['cfg'] = cfg.parse_file(f)
    else:
        logging.error('Missing configuration file')
        return app

    logging.basicConfig(
        level=app['cfg'].logging.level,
        format=app['cfg'].logging.message_format
    )

    app.router.add_get('/', index_handler)
    app.router.add_post('/submit', submit_handler)

    return app
