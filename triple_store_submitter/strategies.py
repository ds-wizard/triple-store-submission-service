import itertools
import logging
import rdflib

from typing import List

from triple_store_submitter.config import SubmitterConfig
from triple_store_submitter.consts import COMMENT_INSTRUCTION_DELIMITER, COMMENT_POST_QUERY_PREFIX, COMMENT_PRE_QUERY_PREFIX


GRAPH_CLASSES = {
    'Graph': rdflib.Graph,
    'ConjunctiveGraph': rdflib.ConjunctiveGraph,
    'QuotedGraph': rdflib.graph.QuotedGraph,
    'Dataset': rdflib.graph.Dataset,
}


def create_graph(class_name: str) -> rdflib.Graph:
    return GRAPH_CLASSES.get(class_name, rdflib.Graph)()


class QueryBuilder:

    def __init__(self):
        self.parts = []  # type: List[str]
        self.pre_queries = []  # type: List[str]
        self.post_queries = []  # type: List[str]

    def add(self, query_part: str):
        self.parts.append(query_part)

    def add_all(self, query_parts: List[str]):
        self.parts.extend(query_parts)

    @property
    def query(self):
        return '\n'.join(itertools.chain(self.pre_queries, self.parts, self.post_queries))

    def extract_extra_queries(self, data: str):
        for line in data.splitlines():
            if line.startswith(COMMENT_PRE_QUERY_PREFIX):
                query = line.split(COMMENT_INSTRUCTION_DELIMITER, maxsplit=1)[1].strip()
                self.pre_queries.append(query)
            if line.startswith(COMMENT_POST_QUERY_PREFIX):
                query = line.split(COMMENT_INSTRUCTION_DELIMITER, maxsplit=1)[1].strip()
                self.post_queries.append(query)

    def delete_graph(self, graph_node):
        self.add(f'DROP SILENT GRAPH {graph_node.n3()} ;')

    def create_graph(self, graph_node):
        self.add(f'CREATE GRAPH {graph_node.n3()} ;')

    def insert_data(self, triples: List[str], graph_node=None):
        if graph_node is None:
            self.add('INSERT DATA {')
            self.add_all(triples)
            self.add('} ;')
        else:
            self.add(f'INSERT DATA {{ GRAPH {graph_node.n3()} {{')
            self.add_all(triples)
            self.add('} } ;')

    def insert_multigraph_start(self):
        self.add('INSERT DATA {')

    def insert_multigraph(self, triples: List[str], graph_node=None):
        self.add(f'GRAPH {graph_node.n3()} {{')
        self.add_all(triples)
        self.add('}')

    def insert_multigraph_finish(self):
        self.add('} ;')

    @staticmethod
    def prepare(cfg: SubmitterConfig, data: str):
        qb = QueryBuilder()
        if cfg.queries.extra_queries:
            qb.extract_extra_queries(data)
        return qb


def basic_query_builder(cfg: SubmitterConfig, data: str, input_format: str) -> str:
    """It will simply inserts triples to a triple store or to a graph based on given type"""
    qb = QueryBuilder.prepare(cfg, data)
    g = create_graph(cfg.triple_store.graph_class)
    g.parse(data=data, format=input_format)

    triples = [
        f'{s.n3()} {p.n3()} {o.n3()} .' for s, p, o in g
    ]

    if cfg.triple_store.graph_named is True and cfg.triple_store.graph_type:
        t = rdflib.URIRef(cfg.triple_store.graph_type)
        graph_node = None
        for s, p, o in g.triples((None, rdflib.RDF.type, t)):
            graph_node = s
        if graph_node is None:
            logging.warning(f'Graph URI not found (type: {t})')

        qb.delete_graph(graph_node)
        qb.create_graph(graph_node)
        qb.insert_data(triples, graph_node=graph_node)
    else:
        qb.insert_data(triples)

    return qb.query


def multi_graph_query_builder(cfg: SubmitterConfig, data: str, input_format: str) -> str:
    """It will inserts the triples for each graph from given quads"""
    qb = QueryBuilder.prepare(cfg, data)
    cg = rdflib.ConjunctiveGraph()
    cg.parse(data=data, format=input_format)

    qb.insert_multigraph_start()
    for ctx in cg.contexts():
        triples = [
            f'{s.n3()} {p.n3()} {o.n3()} .' for s, p, o in cg.triples((None, None, None), context=ctx)
        ]
        qb.insert_multigraph(triples=triples, graph_node=ctx.identifier)
    else:
        logging.warning(f'No graphs found in given RDF')
    qb.insert_multigraph_finish()

    return qb.query


QUERY_BUILDER_STRATEGIES = {
    'basic': basic_query_builder,
    'multi-graph': multi_graph_query_builder,
}


def build_query(cfg: SubmitterConfig, data: str, input_format: str) -> str:
    query_strategy = QUERY_BUILDER_STRATEGIES.get(cfg.queries.strategy, basic_query_builder)
    return query_strategy(cfg, data, input_format)
