import importlib
import os
import pkgutil
import warnings
import typing as tp

__all__ = ['import_from', 'import_class']


def import_class(path: str) -> type:
    """
    Import a class identified with given module path and class name

    :param path: path, eg. subprocess.Popen
    :return: imported class
    """
    *path, classname = path.split('.')
    import_path = '.'.join(path)
    try:
        return getattr(importlib.import_module(import_path), classname)
    except AttributeError:
        raise ImportError('%s not found in %s' % (classname, import_path))


def import_from(path: tp.List[str], package_prefix: str, all_: tp.List[str],
                locals: tp.Dict[str, tp.Any], recursive: bool = True,
                fail_on_attributerror: bool = True, create_all: bool = True,
                skip_single_underscores: bool = True,
                skip_not_having_all: bool = False) -> None:
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
    :param create_all: whether to create artificial __all__'s for modules that don't have them
    :param skip_single_underscores: whether to refrain from importing things that are preceded with a single underscore.
        Pertains to modules, as well as items
    :param skip_not_having_all: skip module's not having an __all__ entry
    :raise AttributeError: module's __all__ contained entry that was not in this module
    """
    for importer, modname, ispkg in pkgutil.walk_packages(path, onerror=lambda x: None):
        if recursive and ispkg:
            if modname.startswith('_') and skip_single_underscores:
                continue
            module = importlib.import_module(package_prefix + '.' + modname)
            try:
                mod_all = module.__all__
            except AttributeError:
                if skip_not_having_all:
                    continue
                mod_all = []
                if create_all:
                    module.__all__ = mod_all
            import_from([os.path.join(path[0], modname)], package_prefix + '.' + modname, mod_all,
                        module.__dict__, recursive=recursive,
                        fail_on_attributerror=fail_on_attributerror, create_all=create_all,
                        skip_not_having_all=skip_not_having_all,
                        skip_single_underscores=skip_single_underscores),
            locals[modname] = module
            if modname not in all_:
                all_.append(modname)
        elif not ispkg:
            module = importlib.import_module(package_prefix + '.' + modname)
            try:
                package_ref = module.__all__
            except AttributeError:
                warnings.warn('Module %s does not contain __all__, enumerating it instead' %
                              (package_prefix + '.' + modname, ), RuntimeWarning)
                package_ref = dir(module)

            for item in package_ref:
                if item.startswith('_') and skip_single_underscores:
                    continue
                try:
                    locals[item] = getattr(module, item)
                except AttributeError:
                    if fail_on_attributerror:
                        raise
                else:
                    if item not in all_:
                        all_.append(item)
