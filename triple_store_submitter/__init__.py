from triple_store_submitter.app import init_func
from triple_store_submitter.consts import PACKAGE_VERSION, PACKAGE_NAME

__version__ = PACKAGE_VERSION
__package_name__ = PACKAGE_NAME
__all__ = ['init_func', '__version__', '__package_name__']
