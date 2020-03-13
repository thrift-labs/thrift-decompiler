import ast
import sys
import pathlib


def parse_ttypes(ctx, thrift_path):
    return None


def parse_constants(ctx, thrift_path):
    return None


def parse_services(ctx, thrift_path):
    return None


def parse_thrift(ctx, thrift_path):
    if not thrift_path.joinpath('__init__.py').exists():
        print(thrift_path, 'is not a python package')
        return None
    # TODO: parse
    thrift_name = thrift_path.name
    print(f'namespace py {thrift_name}')
    ctx['thrift_name'] = thrift_name

    services = None
    ttypes = None
    constants = None
    for path in thrift_path.iterdir():
        if path.is_file() and path.name.endswith('.py'):
            if path.name  == 'ttypes.py':
                ttypes = parse_ttypes(ctx, path)
            elif path.name == 'constants.py':
                constants = parse_constants(ctx, path)
            elif path.name == '__init__.py':
                pass
            else:
                service_name = path.name.strip('.py')
                print(f'has service{service_name}')
                services = parse_services(ctx, path)

    includes = []
    for path in thrift_path.iterdir():
        if path.is_dir():
            thrift = parse_thrift(ctx, path)
            includes.append(thrift)

    return (ttypes, constants, services, includes)


def make_thriftfile(thrift):
    pass


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
            thrift = parse_thrift(ctx, path)
            make_thriftfile(thrift)


if __name__ == '__main__':
    gen_py_path = sys.argv[1]
    main(gen_py_path)
