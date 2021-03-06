
PACKAGE_NAME = 'triple_store_submitter'
NICE_NAME = 'DSW Triple Store Submission Service'
PACKAGE_VERSION = '1.2.0'
ENV_CONFIG = 'SUBMISSION_CONFIG'

_DEFAULT_BUILT_AT = 'BUILT_AT'
BUILT_AT = '--BUILT_AT--'
_DEFAULT_VERSION = 'VERSION'
VERSION = '--VERSION--'

DEFAULT_ENCODING = 'utf-8'

COMMENT_INSTRUCTION_DELIMITER = ':'
COMMENT_PRE_QUERY_PREFIX = '#> pre-query:'
COMMENT_POST_QUERY_PREFIX = '#> post-query:'


class BuildInfo:

    name = NICE_NAME
    built_at = BUILT_AT if BUILT_AT != f'--{_DEFAULT_BUILT_AT}--' else 'unknown'
    version = VERSION if VERSION != f'--{_DEFAULT_VERSION}--' else 'unknown'
    package_version = PACKAGE_VERSION

    @classmethod
    def obj(cls):
        return {
            'name': cls.name,
            'package_version': cls.package_version,
            'version': cls.version,
            'built_at': cls.built_at,
        }
