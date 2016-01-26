import json
from collections import Mapping
from pprint import pformat


class PrettyPrinter(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skipkeys = True
        self.ensure_ascii = False
        self.indent = 4
        self.separators = (',', ': ')
        self.sort_keys = True

    def default(self, obj):
        print(type(obj), obj.__dict__)

        def dictfilter(d):
            return {k: v for k, v, in d.items() if True or not isinstance(k, str) or not k.startswith('_')}

        if isinstance(obj, Mapping):
            return dictfilter(dict(obj))

        if hasattr(obj, '__dict__'):
            return dictfilter(obj.__dict__)

        return pformat(obj)


def ppp(obj):
    def debug(o):
        print('{0}Possible unknown object{0}type({1}){0}dir({2}){0}str({3}){0}'.format(
            '\n-------------\n',
            type(o),
            dir(o),
            str(o)))

    def f(o):
        if o is None or isinstance(o, (str, int)):
            return o
        elif callable(o):
            return str(o)
        elif isinstance(o, (list, tuple)):
            return [f(v) for v in o]
        elif isinstance(o, dict):
            return {f(k): f(v) for k, v in o.items()}
        # debug(o)
        if hasattr(o, '__class__'):
            return f({k: getattr(o, k) for k in dir(o) if hasattr(o, k) and not k.startswith('_')})
        else:
            return pformat(o)

    print(json.dumps(f(obj), skipkeys=True, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True))
    # print(f(obj))


def print_mro(obj):
    from inspect import getmro
    print(getmro(type(obj)))


def write(obj, fp, *args, **kwargs):
    return json.dump(obj, fp, cls=PrettyPrinter, *args, **kwargs)


def get(obj, *args, **kwargs):
    return json.dumps(obj, cls=PrettyPrinter, *args, **kwargs)


def stdout(obj, *args, **kwargs):
    print(get(obj, *args, **kwargs))
