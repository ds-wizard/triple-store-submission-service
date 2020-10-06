# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Possibility to specify type of graph used with rdflib
- Strategies for building SPARQL query:
  - `basic` = previous functionaly (default)
  - `multi-graph` = when there are multiple graphs to be inserted
- Extra queries from special comments
- Support of various input RDF formats based on `Content-Type` headers

## [1.1.0]

### Added

- Configurable SPARQL authentication method for the endpoint

## [1.0.0]

Initial version for simple inserts into triple stores via SPARQL query.

### Added

- Ability to accept RDF Turtle file, transform it into SPARQL INSERT query
  and submit it to configured SPARQL endpoint
- Optional use of named graph that is purged upon insertion
- Optional security using configured token

[Unreleased]: /../../compare/v1.1.0...develop
[1.0.0]: /../../tree/v1.0.0
[1.1.0]: /../../tree/v1.1.0