import importlib, sys, os, argparse
from abc import ABC

def generate_parser(prog, module_dir, abstract_name):
    """
    abstract_name must point to an abstract class that defines a generate_subparser method
    """

    # Generate a base parser
    parser = argparse.ArgumentParser(prog=prog, description="A CLI interface for report processing and generation for ACM/OCM Integration tests and consumers.")
    subparser = parser.add_subparsers(dest="generator_name", required=True,
        title=f"{module_dir.capitalize()} Subcommands", description=f"Report generation utilities accessable via the {prog} CLI.")

    # Load and bootstrap subparsers from each class in module_dir
    # Trick for module loading from https://stackoverflow.com/a/30605712
    modules = os.listdir(module_dir)

    # Remove __init__.py and the abstract parent class
    if '__init__.py' in modules: modules.remove('__init__.py')
    if f"{abstract_name}.py" in modules: modules.remove(f"{abstract_name}.py")

    # Load in our Abstract class to verify that we only pull in implementations of that class
    abstract_module = importlib.import_module(f".{abstract_name}", module_dir)
    abstract_class = getattr(abstract_module, abstract_name)

    # Maintain a dict of subparser to class mappings
    subparser_mappings = {}

    for module in modules:
        if module.split('.')[-1] == 'py':
            mod_name=module.replace('.py', '')
            if os.getenv("DEBUG"): 
                print(f"Detected a module with - Name: {mod_name}, Package: {module_dir}")
            # Load the module and grab its class
            mod = importlib.import_module(f".{mod_name}", module_dir)
            module_class = getattr(mod, mod_name)
            # If its a subclass of our abstract class, bootstrap it.
            if issubclass(module_class, abstract_class):
                sp_name, sp = module_class.generate_subparser(subparser)
                if sp.get_default("func") is None:
                    sp.set_defaults(func=default_handler)
                subparser_mappings[sp_name] = module_class
                if os.getenv("DEBUG"): 
                    print(f"Adding subparser for module with Name: {mod_name}, Package: {module_dir}")
            else:
                if os.getenv("DEBUG"): 
                    print(f"Module with Name: {mod_name}, Package: {module_dir} is not a subclass of {abstract_name}, skipping.")
    # Return our built parser and subparser mappings
    return parser, subparser_mappings


def default_handler(args):
    print("Using the default handler for subparsers, if you want your module to do something special, use .set_default(func=<your-function>) in your generate_subparser function.")
    print("Printing details of invocation below.\n")
    args_dict = vars(args)
    print(f"Subparser {args.generator_name} called with arguments:")
    for attr in args_dict.keys():
        if attr != "func":
            print(f"\t{attr}: {args_dict[attr]}")


if __name__ == '__main__':
    parser, subparser_mappings = generate_parser(sys.argv[0], 'generators', 'AbstractGenerator')
    parsed_args = parser.parse_args(sys.argv[1:])
    parsed_args.func(parsed_args)
