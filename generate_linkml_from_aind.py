import importlib
import pydantic
import enum
import inspect

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import EnumDefinition
from linkml_runtime.utils.schemaview import PermissibleValue, PermissibleValueText
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


def populate_enum(sb: SchemaBuilder, enum_name: str, enum_object: enum.Enum):
    """Populate a LinkML SchemaBuilder instance with a new enum derived from a pydantic Enum object."""
    try:
        sb.add_enum(
            EnumDefinition(
                name=enum_name,
                permissible_values=dict(
                    (attribute, getattr(enum_object, attribute).value) for attribute in dir(enum_object) if
                    not attribute.startswith('__'))
            )
        )
    except ValueError as e:
        if not 'already exists' in str(e):
            raise


def populate_basemodel(sb: SchemaBuilder, basemodel_name: str, basemodel_object: pydantic.BaseModel):
    sb.add_class(
        basemodel_name,
        slots=basemodel_object.model_fields,
        is_a=basemodel_object.__mro__[1].__name__,
        class_uri=f'schema:{basemodel_name}',
        description=basemodel_object.__doc__.strip() if basemodel_object.__doc__ else "No description"
    )


def populate_schema_builder_from_module(sb: SchemaBuilder, module: str):
    for module in get_all_modules(imported_modules=list(), root_module_name=module):
        for class_name, class_object in inspect.getmembers(module, inspect.isclass):
            if issubclass(class_object, enum.Enum):
                populate_enum(sb, class_name, class_object)
            elif issubclass(class_object, pydantic.BaseModel):
                populate_basemodel(sb, class_name, class_object)


def main():
    sb = SchemaBuilder()
    populate_schema_builder_from_module(sb, module='aind_data_schema.models')
    yml = yaml_dumper.dumps(sb.schema)
    with open('generated_linkml_models/aind.yml', 'w') as f:
        f.write(yml)
    print('Success!')


if __name__ == '__main__':
    main()
