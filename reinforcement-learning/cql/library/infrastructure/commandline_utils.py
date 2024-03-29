import argparse
import inspect

import docstring_parser


def get_argparser_from_func(func, parser, exclude=None):
    """ Read the argument of a function and parse it as ArgumentParser. """
    if parser is None:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    signature = inspect.signature(func)
    docstring = docstring_parser.parse(inspect.getdoc(func))

    # transform docstring.params to dictionary
    params = {p.arg_name: p.description for p in docstring.params}

    if exclude is None:
        exclude = []

    exclude.extend(['self', 'cls', 'args', 'kwargs'])

    for k, v in signature.parameters.items():
        if k in exclude:
            continue
        if v.default is inspect.Parameter.empty:
            parser.add_argument('--' + k, help=params.get(k, ' '), required=True)
        else:
            if isinstance(v.default, bool):
                if not v.default:
                    action = 'store_true'
                else:
                    action = 'store_false'
                parser.add_argument('--' + k, action=action, help=params.get(k, ' '))
            else:
                if v.default is not None:
                    arg_type = type(v.default)
                elif v.annotation != inspect.Signature.empty:
                    # get from annotation
                    arg_type = v.annotation
                else:
                    raise ValueError(
                        f'Argument with default value None must be annotated with type in {func}, {k}, {v.annotation}')
                parser.add_argument('--' + k, type=arg_type, default=v.default, help=params.get(k, ' '))
    return parser


def run_func_as_main(func, parser=None, passed_args=None):
    """ Run function as the main. Put the function arguments into argument parser """
    if passed_args is None:
        passed_args = {}
    parser = get_argparser_from_func(func, parser=parser, exclude=list(passed_args.keys()))
    args = vars(parser.parse_args())
    args.update(passed_args)
    func(**args)
