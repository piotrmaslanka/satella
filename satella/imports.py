import typing as tp
import importlib
import pkgutil
import logging
import os

__all__ = ['import_from']

logger = logging.getLogger(__name__)


def import_from(path: tp.List[str], package_prefix: str, all_: tp.List[str], locals: tp.Dict[str, tp.Any], recursive: bool = True,
                fail_on_attributerror: bool = True, add_all: bool = True) -> None:
    """
    Import everything from a given module. Append these module's all to.

    This will examine __all__ of given module (if it has any, else it will just import everything
    from it, which is probably a bad practice and will heavily pollute the namespace.

    As a side effect, this will equip all of your packages with __all__.

    :param path: module's __path__
    :param package_prefix: package prefix to import from. Use __name__
    :param all_: module's __all__ to append to
    :param recursive: whether to import packages as well
    :param fail_on_attributerror: whether to fail if a module reports something in their __all__ that
        is physically not there (ie. getattr() raised AttributeError
    :param locals: module's locals, obtain them by calling locals() in importing module's context
    :param add_all: whether to create artificial __all__'s for modules that don't have them
    :raise AttributeError: module's __all__ contained entry that was not in this module
    """
    logger.warning('Invoking with path=%s', path)
    for importer, modname, ispkg in pkgutil.walk_packages(path, onerror=lambda x: None):
        if recursive and ispkg:
            module = importlib.import_module(package_prefix+'.'+modname)
            logger.warning(repr(package_prefix))
            logger.warning(repr(modname))
            try:
                mod_all = module.__all__
            except AttributeError:
                mod_all = []
                if add_all:
                    module.__all__ = mod_all
            import_from([os.path.join(path[0], modname)], package_prefix+'.'+modname, mod_all, module.__dict__, recursive=recursive, fail_on_attributerror=fail_on_attributerror),
            locals[modname] = module
            __all__.append(modname)
        elif not ispkg:
            module = importlib.import_module(package_prefix+'.'+modname)
            try:
                package_ref = module.__all__
            except AttributeError:
                logger.warning('Module %s does not contain __all__, enumerating it instead', package_prefix+'.'+modname)
                package_ref = dir(module)

            for item in package_ref:
                try:
                    locals[item] = getattr(module, item)
                except AttributeError:
                    if fail_on_attributerror:
                        raise
                else:
                    all_.append(item)
