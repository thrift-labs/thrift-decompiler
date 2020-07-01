import ast
import sys
import pathlib
import io
from copy import deepcopy


def load_ast(thrift_path):
    with io.open(thrift_path, 'r') as f:
        return ast.parse(f.read())

def parse_ttypes(ctx, thrift_path):
    ast_file = load_ast(thrift_path)

    classdefs = []
    for x in ast_file.body:
        if isinstance(x, ast.ClassDef):
            classdefs.append(x)

    ttypes = []
    for x in classdefs:
        is_enum = read_as_enum(x)
        if is_enum:
            ttypes.append((x, is_enum))
            continue
        args = read_thrift_spec(x)
        ttypes.append((x, args))
    return ttypes


def parse_constants(ctx, thrift_path):
    pass


def read_method(classdef):
    funcdefs = []
    for x in classdef.body:
        if isinstance(x, ast.FunctionDef):
            funcdefs.append(x)
    methods = []
    for x in funcdefs:
        args = [
            arg.arg
            for arg in x.args.args
        ]
        method = (x.name, args)
    return method


def read_thrift_spec(classdef):
    thrift_spec = None
    for x in classdef.body:
        if isinstance(x, ast.Assign):
            if len(x.targets) == 1 and x.targets[0].id == 'thrift_spec':
                thrift_spec = x
                break
    if not thrift_spec:
        return
    '''
      def validate(self):
        if self.a is None:
          raise TProtocol.TProtocolException(message='Required field a is unset!')
        return
    '''
    args = []
    for e in thrift_spec.value.elts:
        # request zero keep
        if isinstance(e, ast.Constant) and e.value is None:
            continue
        # (2, TType.I64, 'b', None, None, ), # 2
        # (1, TType.STRUCT, 'param', (AddParam, AddParam.thrift_spec), None, ), # 1
        index = e.elts[0].value
        # types
        assert isinstance(e.elts[1], ast.Attribute)
        types = e.elts[1].attr
        name = e.elts[2].value
        struct_name = None
        if types == 'STRUCT':
            struct_name = e.elts[3].elts[0].id
        default = e.elts[4].value

        arg = (index, types, name, struct_name, default)
        args.append(arg)
    return args


def read_as_enum(classdef):
    assigns = []
    for x in classdef.body:
        if isinstance(x, ast.Assign):
            assigns.append(x)

    is_enum = False
    for x in assigns:
        if x.targets[0].id == '_NAMES_TO_VALUES':
            is_enum = True
            break
    # TODO parse more
    return is_enum


def parse_services(ctx, thrift_path):
    ast_file = load_ast(thrift_path)

    classdefs = []
    for x in ast_file.body:
        if isinstance(x, ast.ClassDef):
            classdefs.append(x)
    # TODO find iface && method
    iface = None
    for x in classdefs:
        if x.name == 'Iface':
            iface = x
            break
    assert iface
    methods = read_method(iface)
    return (classdefs, methods)


def parse_thrift(ctx, thrift_path):
    if not thrift_path.joinpath('__init__.py').exists():
        print(thrift_path, 'is not a python package')
        return None
    # TODO: parse
    thrift_name = thrift_path.name
    origin = ctx.get('thrift_name')
    if origin:
        thrift_name = f'{origin}.{thrift_name}'
    print(f'namespace py {thrift_name}')
    ctx['thrift_name'] = thrift_name
    services = None
    ttypes = None
    constants = None
    for path in thrift_path.iterdir():
        if path.is_file() and path.name.endswith('.py'):
            if path.name  == 'ttypes.py':
                ttypes = parse_ttypes(deepcopy(ctx), path)
            elif path.name == 'constants.py':
                constants = parse_constants(deepcopy(ctx), path)
            elif path.name == '__init__.py':
                pass
            else:
                service_name = path.name.strip('.py')
                print(f'has service {service_name}')
                services = parse_services(deepcopy(ctx), path)

    includes = []
    for path in thrift_path.iterdir():
        if path.is_dir():
            thrift = parse_thrift(deepcopy(ctx), path)
            includes.append(thrift)

    return (ttypes, constants, services, includes)


def make_thriftfile(thrift):
    print(thrift)


def main(gen_py_path):
    '''
    1. 检测 gen-py 下目录
    '''
    gen_py = pathlib.Path(gen_py_path)
    if not gen_py.joinpath('__init__.py').exists():
        print('not a gen-py package')
        return

    ctx = {}
    for path in gen_py.iterdir():
        if path.is_dir():
            #import pdb
            #pdb.set_trace()
            thrift = parse_thrift(ctx, path)
            make_thriftfile(thrift)


if __name__ == '__main__':
    gen_py_path = sys.argv[1]
    main(gen_py_path)
