import importlib
import pydantic
import enum
import inspect

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import EnumDefinition
from linkml_runtime.utils.schemaview import SchemaView, ElementName, PermissibleValue, PermissibleValueText
from linkml_runtime.utils.schema_builder import SchemaBuilder
from linkml_runtime.dumpers import yaml_dumper


def get_all_modules(imported_modules: list, root_module_name: str):
    try:
        module = importlib.import_module(root_module_name)
        imported_modules.append(module)
        for submodule_filename in module.__loader__.get_resource_reader().contents():
            if submodule_filename.endswith('.py') and not submodule_filename.startswith('__'):
                get_all_modules(imported_modules, f'{root_module_name}.{submodule_filename[:-len(".py")]}')
    except ModuleNotFoundError:
        return imported_modules
    return imported_modules


def populate_schema_builder_from_module(sb: SchemaBuilder, module: str):
    for module in get_all_modules(imported_modules=list(), root_module_name='aind_data_schema.models'):
        for class_name, class_object in inspect.getmembers(module, inspect.isclass):
            if issubclass(class_object, enum.Enum):
                try:
                    sb.add_enum(
                        EnumDefinition(
                            name=class_name,
                            permissible_values=dict(
                                (attribute, getattr(class_object, attribute).value) for attribute in dir(class_object) if
                                not attribute.startswith('__')),
                        )
                    )
                except ValueError:
                    pass
            elif issubclass(class_object, pydantic.BaseModel):
                sb.add_class(
                    class_name,
                    slots=class_object.model_fields,
                    is_a=class_object.__mro__[1].__name__,
                    class_uri=f'schema:{class_name}',
                    description=class_object.__doc__.strip() if class_object.__doc__ else "No description"
                )


def main():
    sb = SchemaBuilder()
    populate_schema_builder_from_module(sb, module='aind_data_schema.models')
    yml = yaml_dumper.dumps(sb.schema)
    with open('simple.yml', 'w') as f:
        f.write(yml)
    print(yml)


if __name__ == '__main__':
    main()
