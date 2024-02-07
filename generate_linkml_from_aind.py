import pprint
import inspect
pp = pprint.PrettyPrinter(indent=4)

import importlib
import inspect
import pydantic
import enum
from linkml_runtime.dumpers import yaml_dumper

def classes_from_module(module_name: str):
    module = importlib.import_module(module_name)
    module_classes = inspect.getmembers(module,
                                 lambda x: inspect.isclass(x) and
                                           issubclass(x, pydantic.BaseModel))
    return module_classes

def enums_from_module(module_name: str):
    """Get pydantic enums

    Parameters
    ----------
    module_name : str
    """
    module = importlib.import_module(module_name)
    module_enums = inspect.getmembers(module,
                                 lambda x: inspect.isclass(x) and
                                           issubclass(x, enum.Enum))
    return module_enums

def write_yaml(module_name: str):
    for klass in classes_from_module(module_name):
        pass
    for enum_obj in enums_from_module(module_name):
        pass

all_slots = list()
with open('simple.yml', 'w') as f:
    f.write('classes:\n')
    for module, classes = classes_from_module('aind_data_schema.models.devices')
    model_name, model_module in module.__dict__.items():
        if not model_name.startswith('__'):
            for model_data_class in inspect.getmembers(model_module, inspect.isclass):
                try:
                    print(modcel_data_class)
                    print(model_data_class[1].__mro__)
                    attributes_in_dataclass = list(model_data_class[1].__annotations__.keys())
                    all_slots += attributes_in_dataclass
                    print(attributes_in_dataclass)
                    if attributes_in_dataclass:
                        f.write(f'  {model_data_class[0]}:\n')
                        f.write(f'    is_a: {model_data_class[1].__mro__[1].__name__}\n')
                        f.write(f'    description: {model_data_class[1].__doc__.strip() or "No description"}\n')
                        f.write(f'    class_uri: schema:{model_data_class[0]}\n')
                        f.write('    attributes:\n')
                        for a in attributes_in_dataclass:
                            f.write(f'      {a}:\n')
                except AttributeError as e:
                    print(e)

print(f'All slots found: {set(all_slots)}')
