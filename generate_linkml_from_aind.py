import importlib
import pydantic
import enum
import inspect

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import EnumDefinition
from linkml_runtime.utils.schemaview import SchemaView, ElementName, PermissibleValue, PermissibleValueText
from linkml_runtime.utils.schema_builder import SchemaBuilder
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

def populate_schema_builder_from_module(sb: SchemaBuilder, module: str = 'aind_data_schema.models.devices'):
    for model_data_class in classes_from_module(module):
        # x = model_data_class[1].__annotations__
        # x = model_data_class[1].model_fields
        # i = model_data_class[1].model_from_schema()
        z = model_data_class[1].__pydantic_core_schema__
        sb.add_class(
            model_data_class[0],
            slots=model_data_class[1].model_fields,
            is_a=model_data_class[1].__mro__[1].__name__,
            class_uri=f'schema:{model_data_class[0]}',
            description=model_data_class[1].__doc__.strip() if model_data_class[1].__doc__ else "No description"
        )
    for model_enum in enums_from_module(module):
        enum_class = model_enum[1]
        sb.add_enum(
            EnumDefinition(
                name=model_enum[0],
                permissible_values=dict((attribute, getattr(enum_class, attribute).value) for attribute in dir(enum_class) if not attribute.startswith('__')),
            )
        )

def main():
    sb = SchemaBuilder()
    devices_module = 'aind_data_schema.models.devices'
    populate_schema_builder_from_module(sb, module=devices_module)
    yml = yaml_dumper.dumps(sb.schema)
    with open('simple.yml', 'w') as f:
        f.write(yml)
    print(yml)

if __name__ == '__main__':
    main()
