import sys
import types
import os.path
try:
    # Python 3.
    import importlib._bootstrap
except ImportError:
    # Python 2.
    import importlib

import pkg_resources
import yaml

class Failure(Exception):
    """Stops execution of a task."""

class Environment(object):
    """Container for settings and other global parameters."""

    __slots__ = ('_states', '__dict__')

    class _context(object):
        def __init__(self, owner, **updates):
            self.owner = owner
            self.updates = updates

        def __enter__(self):
            self.owner.push(**self.updates)

        def __exit__(self, exc_type, exc_value, exc_tb):
            self.owner.pop()

    def __init__(self, **updates):
        self._states = []
        self.add(**updates)

    def clear(self):
        self.__dict__.clear()

    def add(self, **updates):
        for key in sorted(updates):
            assert not key.startswith('_'), \
                    "parameter should not start with '_': %r" % key
            assert key not in self.__dict__, \
                    "duplicate parameter %r" % key
            self.__dict__[key] = updates[key]

    def set(self, **updates):
        for key in sorted(updates):
            assert key in self.__dict__, \
                    "unknown parameter %r" % key
            self.__dict__[key] = updates[key]

    def push(self, **updates):
        self._states.append(self.__dict__)
        self.__dict__ = self.__dict__.copy()
        self.set(**updates)

    def pop(self):
        assert self._states, "unbalanced pop()"
        self.__dict__ = self._states.pop()

    def __call__(self, **updates):
        return self._context(self, **updates)

from .log import warn, debug, fail

env = Environment()

def task(T, is_default=False):
    """Registers the wrapped function/class as a task."""
    assert isinstance(T, (types.FunctionType, type)), \
            "a task must be either a function or a class"

    # Convert functions/old-style classes to a new-style class.
    if isinstance(T, types.FunctionType):
        T_dict = {}
        T_dict['__module__'] = T.__module__
        T_dict['__doc__'] = T.__doc__
        T_dict['_fn'] = staticmethod(T)
        T_dict['_vararg'] = None
        def __init__(self, **params):
            self._params = params
        T_dict['__init__'] = __init__
        def __call__(self):
            args = ()
            kwds = self._params.copy()
            if self._vararg:
                args = tuple(kwds.pop(self._vararg))
            return self._fn(*args, **kwds)
        T_dict['__call__'] = __call__
        params, varargs, varkeywords = _introspect(T)
        for param in params:
            if isinstance(param, str):
                T_dict[param] = argument()
            else:
                param, default = param
                T_dict[param] = argument(default=default)
        if varargs:
            T_dict[varargs] = argument(default=(), plural=True)
            T_dict['_vararg'] = varargs
        norm_T = type(T.__name__, (object,), T_dict)
    else:
        norm_T = T

    # Process arguments and options.
    args = []
    opts = []
    attrs = {}
    for C in reversed(norm_T.__mro__):
        attrs.update(C.__dict__)
    arg_attrs = []
    opt_attrs = []
    for attr in sorted(attrs):
        value = attrs[attr]
        if isinstance(value, argument):
            arg_attrs.append((value.order, attr, value))
        if isinstance(value, option):
            opt_attrs.append((value.order, attr, value))
    arg_attrs.sort()
    opt_attrs.sort()
    names = set()
    keys = set()
    for order, attr, dsc in arg_attrs:
        name = _to_name(attr)
        assert name not in names, \
                "duplicate argument name: <%s>" % name
        names.add(name)
        check = dsc.check
        default = dsc.default
        is_plural = dsc.plural
        is_optional = True
        if default is dsc.REQ:
            is_optional = False
            default = None
        spec = ArgSpec(attr, name, check, default=default,
                       is_optional=is_optional, is_plural=is_plural)
        args.append(spec)
    for order, attr, dsc in opt_attrs:
        name = _to_name(attr)
        assert name not in names, \
                "duplicate option name: --%s" % name
        names.add(name)
        key = dsc.key
        if key is not None:
            assert key not in keys, \
                    "duplicate option name: -%s" % key
            keys.add(key)
        check = dsc.check
        default = dsc.default
        is_plural = dsc.plural
        has_value = True
        value_name = (dsc.value_name or name).upper()
        if default is dsc.NOVAL:
            has_value = False
            value_name = None
            default = False
        hint = dsc.hint
        spec = OptSpec(attr, name, key, check, default, is_plural=is_plural,
                       has_value=has_value, value_name=value_name, hint=hint)
        opts.append(spec)

    # Extract the name and description.
    name = _to_name(norm_T.__name__)
    if is_default:
        name = ''
    hint, help = _describe(norm_T)

    # Register the task.
    spec = TaskSpec(name, norm_T, args, opts, hint=hint, help=help)
    env.task_map[name] = spec
    return T

def default_task(T):
    """Registers the wrapped function/class as the default task."""
    return task(T, True)

def setting(S):
    """Registers the wrapped function as a setting."""
    assert isinstance(S, types.FunctionType), \
            "a setting must be a function"

    # Extract and verify the parameter.
    params, varargs, varkeywords = _introspect(S)
    assert (len(params) >= 1 and len(params[0]) == 2) or varargs, \
            "a setting must accept zero or one parameter"
    has_value = (not params or params[0][1] is not False)
    value_name = (params and params[0][0] or varargs).upper()

    # Extract the name and description.
    name = _to_name(S.__name__)
    hint, help = _describe(S)

    # Register the setting.
    spec = SettingSpec(name, S, has_value=has_value, value_name=value_name,
                       hint=hint, help=help)
    env.setting_map[name] = spec
    return S

def topic(T):
    """Registers the wrapped function as a help topic."""
    assert isinstance(T, types.FunctionType), \
            "a topic must be a function"

    # Verify that there are no parameters.
    params, varargs, varkeywords = _introspect(T)
    assert not params or len(params[0]) == 2, \
            "a topic must accept no parameters"

    # Extract the name and description.
    name = _to_name(T.__name__)
    hint, help = _describe(T)

    # Register the topic.
    spec = TopicSpec(name, T, hint=hint, help=help)
    env.topic_map[name] = spec
    return T

class argument(object):
    """Describes a task argument."""

    CTR = itertools.count(1)
    REQ = object()

    def __init__(self, check=None, default=REQ, plural=False):
        assert isinstance(plural, bool)
        self.check = check
        self.default = default
        self.plural = plural
        self.order = next(self.CTR)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        raise AttributeError("unset argument")

class option(object):
    """Describes a task option."""

    CTR = itertools.count(1)
    NOVAL = object()

    def __init__(self, key=None, check=None, default=NOVAL, plural=False,
                 value_name=None, hint=None):
        assert key is None or (isinstance(key, str) and
                               re.match(r'^[a-zA-Z]$', key)), \
                "key must be a letter, got %r" % key
        assert isinstance(plural, bool)
        assert value_name is None or isinstance(value_name, str)
        assert hint is None or isinstance(hint, str)
        self.key = key
        self.check = check
        self.default = default
        self.plural = plural
        self.value_name = value_name
        self.hint = hint
        self.order = next(self.CTR)

def _to_name(keyword):
    # Convert an identifier or a keyword to a task/setting name.
    return keyword.lower().replace(' ', '-').replace('_', '-')

def _introspect(fn):
    # Find function parameters and default values.
    params = []
    varargs = None
    varkeywords = None
    code = fn.__code__
    defaults = fn.__defaults__ or ()
    idx = 0
    while idx < code.co_argcount:
        name = code.co_varnames[idx]
        if idx < code.co_argcount-len(defaults):
            params.append(name)
        else:
            default = defaults[idx-code.co_argcount+len(defaults)]
            params.append((name, default))
        idx += 1
    if code.co_flags & 0x04: # CO_VARARGS
        varargs = code.co_varnames[idx]
        idx += 1
    if code.co_flags & 0x08: # CO_VARKEYWORDS
        varkeywords = code.co_varnames[idx]
        idx += 1
    return params, varargs, varkeywords

def _describe(fn):
    # Convert a docstring to a hint line and a description.
    hint = ""
    help = ""
    doc = fn.__doc__
    if doc:
        doc = doc.strip()
    if doc:
        lines = doc.splitlines()
        hint = lines.pop(0).strip()
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop(-1)
        indent = None
        for line in lines:
            short_line = line.lstrip()
            if short_line:
                line_indent = len(line)-len(short_line)
                if indent is None or line_indent < indent:
                    indent = line_indent
        if indent:
            lines = [line[indent:] for line in lines]
        help = "\n".join(lines)
    return hint, help

# Al final del archivo
import neocogs
neocogs.env = env
neocogs.task = task
neocogs.default_task = default_task
neocogs.setting = setting
neocogs.topic = topic
neocogs.argument = argument
neocogs.option = option
neocogs.Failure = Failure
neocogs.Environment = Environment
