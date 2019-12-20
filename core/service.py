import importlib
import pkgutil

# Package containing all the modules for import
from service import payload
from service import connector
from common import logger

logger = logger.init(__name__)


def get_payloads_meta() -> dict:
    result = dynamic_import(payload, ['service', 'command', 'command_steps'], 'command')
    return result


def get_connectors_meta() -> dict:
    result = dynamic_import(connector, ['service', 'consumer_key', 'consumer_secret', 'endpoints'], 'service')
    return result


def dynamic_import(package: object, required_meta_keys: list, result_key: str):
    result = {}
    for importer, module_name, is_package in pkgutil.iter_modules(package.__path__):
        if '__init__' not in module_name:
            module = importlib.import_module('{0}.{1}'.format(package.__name__, module_name))
            if 'META' in dir(module):
                meta = getattr(module, 'META')
                check = [key for key in required_meta_keys if key not in meta]
                if len(check) > 0:
                    logger.warning('Module \'{0}\' is missing required meta data \'{1}\' and going to be skipped!'.
                                   format(module.__name__, check))
                    continue
                check = [key for key in required_meta_keys if (meta[key] is None or meta[key] == '')]
                if len(check) > 0:
                    logger.warning('Module \'{0}\' is missing values in meta data \'{1}\' and going to be skipped!'.
                                   format(module.__name__, check))
                    continue
                else:
                    meta['module'] = module.__name__
                    result[meta[result_key]] = {
                        'meta': meta,
                    }
                    logger.info(
                        'Imported metadata for module \'{0}\' from the \'{1}\' package...'
                        .format(module_name, package.__name__))
            else:
                logger.warning('Module \'{0}\' metadata not found, skipping...'.format(module.__name__))
    return result
