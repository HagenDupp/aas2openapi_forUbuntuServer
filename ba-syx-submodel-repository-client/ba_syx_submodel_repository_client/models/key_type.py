from enum import Enum


class KeyType(str, Enum):
    ANNOTATED_RELATIONSHIP_ELEMENT = "ANNOTATED_RELATIONSHIP_ELEMENT"
    ASSET_ADMINISTRATION_SHELL = "ASSET_ADMINISTRATION_SHELL"
    BASIC_EVENT_ELEMENT = "BASIC_EVENT_ELEMENT"
    BLOB = "BLOB"
    CAPABILITY = "CAPABILITY"
    CONCEPT_DESCRIPTION = "CONCEPT_DESCRIPTION"
    DATA_ELEMENT = "DATA_ELEMENT"
    ENTITY = "ENTITY"
    EVENT_ELEMENT = "EVENT_ELEMENT"
    FILE = "FILE"
    FRAGMENT_REFERENCE = "FRAGMENT_REFERENCE"
    GLOBAL_REFERENCE = "GLOBAL_REFERENCE"
    IDENTIFIABLE = "IDENTIFIABLE"
    MULTI_LANGUAGE_PROPERTY = "MULTI_LANGUAGE_PROPERTY"
    OPERATION = "OPERATION"
    PROPERTY = "PROPERTY"
    RANGE = "RANGE"
    REFERABLE = "REFERABLE"
    REFERENCE_ELEMENT = "REFERENCE_ELEMENT"
    RELATIONSHIP_ELEMENT = "RELATIONSHIP_ELEMENT"
    SUBMODEL = "SUBMODEL"
    SUBMODEL_ELEMENT = "SUBMODEL_ELEMENT"
    SUBMODEL_ELEMENT_COLLECTION = "SUBMODEL_ELEMENT_COLLECTION"
    SUBMODEL_ELEMENT_LIST = "SUBMODEL_ELEMENT_LIST"

    def __str__(self) -> str:
        return str(self.value)