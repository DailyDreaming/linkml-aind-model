import importlib
import pydantic
import enum
import inspect

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import EnumDefinition, SlotDefinition
from linkml_runtime.utils.schemaview import PermissibleValue, PermissibleValueText
from linkml_runtime.utils.schema_builder import SchemaBuilder
from linkml_runtime.dumpers import yaml_dumper
from typing import Type, List


# BICAN already has linkml here: https://github.com/brain-bican/models/tree/main/linkml-schema
# Biolink also has linkml: https://github.com/biolink/biolink-model/blob/master/src/biolink_model/schema/biolink_model.yaml
# openminds is JSON: https://github.com/openMetadataInitiative/openMINDS_core/tree/v4
# ATOM: https://bioportal.bioontology.org/ontologies/ATOM
# ATOM: https://github.com/SciCrunch/NIF-Ontology/blob/atlas/ttl/atom.ttl
# ATOM: https://www.nature.com/articles/s41597-023-02389-4
KNOWN_MODELS = {
    'dandi': 'dandischema.models',
    'aind': 'aind_data_schema.models'
}


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
                    not attribute.startswith('__') and isinstance(getattr(enum_object, attribute), enum.Enum))
            )
        )
    except ValueError as e:
        if not 'already exists' in str(e):
            raise


def populate_basemodel(sb: SchemaBuilder, basemodel_name: str, basemodel_object: pydantic.BaseModel):
    sb.add_class(
        basemodel_name,
        slots=basemodel_object.__annotations__,
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


def slots_builder_from_model(model: Type[pydantic.BaseModel]) -> List[SlotDefinition]:

    slot_names = model.__annotations__

    if len(slot_names) == 0:
        return []

    # Generate the Pydandic core schema of the model
    core_schema = model.__pydantic_core_schema__

    # Find the core schema that represents the model
    # For some reason, the core schema that represents the model can be nested though
    # not always
    model_core_schema = core_schema
    while True:
        if model_core_schema['type'] == 'model':
            break
        else:
            model_core_schema = model_core_schema['schema']

    assert model_core_schema['schema']["type"] == 'model-fields'

    # The dictionary of the fields in the model paired with their core schema
    fields_core_schema = model_core_schema['schema']['fields']

    slots = []
    for slot_name in slot_names:
        # The core schema of the field in the Pydantic model corresponding to the slot
        field_schema = fields_core_schema[slot_name]['schema']

        # todo: more to be done with the slot creation based on the information contained
        #  in the `field_schema`
        slot = SlotDefinition(slot_name)

        slots.append(slot)

    return slots


def main():
    org = 'dandi'
    sb = SchemaBuilder()
    populate_schema_builder_from_module(sb, module=KNOWN_MODELS[org])
    yml = yaml_dumper.dumps(sb.schema)
    with open(f'generated_linkml_models/{org}.yml', 'w') as f:
        f.write(yml)
    print('Success!')


if __name__ == '__main__':
    main()
