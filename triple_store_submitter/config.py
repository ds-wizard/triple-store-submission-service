import yaml

from typing import List


class MissingConfigurationError(Exception):

    def __init__(self, missing: List[str]):
        self.missing = missing


class TripleStoreConfig:

    def __init__(self, sparql_endpoint: str, auth_method: str, auth_username: str,
                 auth_password: str, graph_class: str, graph_named: str, graph_type: str):
        self.sparql_endpoint = sparql_endpoint
        self.auth_method = auth_method
        self.auth_username = auth_username
        self.auth_password = auth_password
        self.graph_class = graph_class
        self.graph_named = graph_named
        self.graph_type = graph_type


class FDPConfig:

    def __init__(self, token: str, distribution: str):
        self.token = token
        self.distribution = distribution


class SecurityConfig:

    def __init__(self, token: str):
        self.token = token


class LoggingConfig:

    def __init__(self, level, message_format: str):
        self.level = level
        self.message_format = message_format


class QueriesConfig:

    def __init__(self, extra_queries: bool, strategy: str):
        self.extra_queries = extra_queries
        self.strategy = strategy


class SubmitterConfig:

    def __init__(self, triple_store: TripleStoreConfig, fdp: FDPConfig,
                 security: SecurityConfig, logging: LoggingConfig,
                 queries: QueriesConfig):
        self.triple_store = triple_store
        self.fdp = fdp
        self.security = security
        self.logging = logging
        self.queries = queries


class SubmitterConfigParser:

    DEFAULTS = {
        'triple-store': {
            'sparql-endpoint': None,
            'auth': {
                'method': 'BASIC',
                'username': None,
                'password': None,
            },
            'graph': {
                'class': 'Graph',
                'named': False,
                'type': None,
            },
        },
        'fdp': {
            'token': None,
            'distribution': None,
        },
        'security': {
            'token': None,
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s | %(levelname)s | %(module)s: %(message)s',
        },
        'queries': {
            'extra-queries': False,
            'strategy': 'basic',
        }
    }

    REQUIRED = [
        ['triple-store', 'sparql-endpoint']
    ]

    def __init__(self):
        self.cfg = dict()

    def has(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return False
            x = x[p]
        return True

    def _get_default(self, *path):
        x = self.DEFAULTS
        for p in path:
            x = x[p]
        return x

    def get_or_default(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return self._get_default(*path)
            x = x[p]
        return x

    def validate(self):
        missing = []
        for path in self.REQUIRED:
            if not self.has(*path):
                missing.append('.'.join(path))
        if len(missing) > 0:
            raise MissingConfigurationError(missing)

    @property
    def _triple_store(self):
        return TripleStoreConfig(
            sparql_endpoint=self.get_or_default('triple-store', 'sparql-endpoint'),
            auth_method=self.get_or_default('triple-store', 'auth', 'method'),
            auth_username=self.get_or_default('triple-store', 'auth', 'username'),
            auth_password=self.get_or_default('triple-store', 'auth', 'password'),
            graph_class=self.get_or_default('triple-store', 'graph', 'class'),
            graph_named=self.get_or_default('triple-store', 'graph', 'named'),
            graph_type=self.get_or_default('triple-store', 'graph', 'type'),
        )

    @property
    def _fdp(self):
        return FDPConfig(
            token=self.get_or_default('fdp', 'token'),
            distribution=self.get_or_default('fdp', 'distribution'),
        )

    @property
    def _security(self):
        return SecurityConfig(
            token=self.get_or_default('security', 'token'),
        )

    @property
    def _logging(self):
        return LoggingConfig(
            level=self.get_or_default('logging', 'level'),
            message_format=self.get_or_default('logging', 'format'),
        )

    @property
    def _queries(self):
        return QueriesConfig(
            extra_queries=self.get_or_default('queries', 'extra-queries'),
            strategy=self.get_or_default('queries', 'strategy'),
        )

    def parse_file(self, fp) -> SubmitterConfig:
        self.cfg = yaml.full_load(fp)
        self.validate()
        return SubmitterConfig(
            triple_store=self._triple_store,
            fdp=self._fdp,
            security=self._security,
            logging=self._logging,
            queries=self._queries,
        )
