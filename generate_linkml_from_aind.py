import os
import sys
import json

import pprint
import inspect
pp = pprint.PrettyPrinter(indent=4)


from aind.src.aind_data_schema.models.devices import Device

import aind_data_schema.models as module


# print(json.dumps(module.__dict__, indent=4))
pp.pprint(module.__dict__)
aind_models = [v for k, v in module.__dict__.items() if not k.startswith('__')]


all_slots = list()
with open('simple.yml', 'w') as f:
    f.write('classes:\n')
    for model_name, model_module in module.__dict__.items():
        if not model_name.startswith('__'):
            for model_data_class in inspect.getmembers(model_module, inspect.isclass):
                try:
                    print(model_data_class)
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


# print()
#
# print(aind_models[0])
# print(inspect.getmembers(aind_models[0]))