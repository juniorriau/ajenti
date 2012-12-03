import os
import inspect
import copy

import ajenti
from ajenti.plugins import manager


class PluginInfo:
    def __init__(self, **kwargs):
        self.author = ''
        self.homepage = ''
        self.dependencies = []

        def init():
            pass

        self.init = init

        for k in kwargs:
            setattr(self, k, kwargs[k])


def plugin(cls):
    if hasattr(cls, 'verify'):
        if not cls.verify():
            return

    if hasattr(cls, 'platforms'):
        if not ajenti.platform in cls.platforms:
            return

    manager.register_implementation(cls)
    cls._plugin = True
    cls._path = inspect.getfile(cls)
    cls.classname = cls.__module__ + '.' + cls.__name__

    def get(cls):
        return manager.get_instance(cls)
    cls.get = get.__get__(cls)

    def new(cls, *args, **kwargs):
        return manager.instantiate(cls, *args, **kwargs)
    cls.new = new.__get__(cls)

    return cls


def _check_plugin(cls):
    if not hasattr(cls, '_plugin'):
        raise Exception('Class %s must be decorated with @plugin' % cls)


def interface(cls):
    def get(cls):
        impls = manager.get_implementations(cls)
        if len(impls) == 0:
            raise Exception('Implementations for %s not found' % cls.__name__)
        return manager.get_instance(impls[0])
    cls.get = get.__get__(cls)

    def get_all(cls):
        return [manager.get_instance(x) for x in manager.get_implementations(cls)]
    cls.get_all = get_all.__get__(cls)

    def get_class(cls):
        return manager.get_implementations(cls)[0]
    cls.get_class = get_class.__get__(cls)

    def get_classes(cls):
        return manager.get_implementations(cls)
    cls.get_classes = get_classes.__get__(cls)

    def get_instances(cls):
        return manager.get_instances(cls)
    cls.get_instances = get_instances.__get__(cls)

    manager.register_interface(cls)

    return cls


def extract_context():
    for frame in inspect.stack():
        self_argument = frame[0].f_code.co_varnames[0]  # This *should* be 'self'
        instance = frame[0].f_locals[self_argument]
        if isinstance(instance, BasePlugin):
            if instance.context is not None:
                return instance.context


class BasePlugin (object):
    default_classconfig = None
    context = None

    def init(self):
        self.context = extract_context()

        if self.context:
            self.classconfig = self.context.user.configs.setdefault(self.classname, copy.deepcopy(self.default_classconfig))

    def open_content(self, path, mode='r'):
        _check_plugin(self.__class__)

        root = os.path.split(self.__class__._path)[0]
        while len(root) > 1 and not os.path.exists(os.path.join(root, 'content')):
            root = os.path.split(root)[0]
        if len(root) <= 1:
            raise Exception('content directory not found')
        return open(os.path.join(root, 'content', path), mode)

    def save_classconfig(self):
        self.context.user.configs[self.classname] = self.classconfig
        ajenti.config.save()


class AppContext (object):
    def __init__(self, context):
        self.session = context.session
        self.user = ajenti.config.tree.users[context.session.identity]


__all__ = [
    'PluginInfo',
    'BasePlugin',
    'AppContext',
    'plugin',
    'extract_context',
    'interface',
]
