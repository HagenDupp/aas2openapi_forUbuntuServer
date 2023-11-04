from aas2openapi.client.aas_client import get_aas_from_server, get_all_aas_from_server
from aas2openapi.util.convert_util import get_vars
from aas2openapi.models import base
from aas2openapi.util import convert_util
from aas2openapi.util.convert_util import get_all_submodel_elements_from_submodel, get_all_submodels_from_model, get_vars
from aas2openapi.util.client_utils import check_aas_and_sm_server_online

import typing
from fastapi import APIRouter
from pydantic import BaseModel, create_model
from pydantic.fields import ModelField, FieldInfo
from pydantic import BaseConfig, validator

from graphene_pydantic import PydanticObjectType, PydanticInputObjectType
import graphene
from starlette_graphene3 import GraphQLApp, make_graphiql_handler, make_playground_handler


from typing import List, Type

def create_graphe_pydantic_output_type_for_model(input_model: Type[BaseModel]) -> PydanticObjectType:
    """
    Creates a pydantic model for the given pydantic model.

    Args:
        model (Type[BaseModel]): Pydantic model for which the Graphene Object Type should be created.

    Returns:
        PydanticObjectType: Graphene Object type for the given pydantic model.
    """
    rework_default_list_to_default_factory(input_model)
    graphene_model = type(input_model.__name__, (PydanticObjectType,), {'Meta': type('Meta', (), {'model': input_model})})
    return graphene_model

# TODO: potentially add query for submodels
# def create_submodel_query(base_query: graphene.ObjectType, submodel: Type[BaseModel]) -> graphene.ObjectType:
#     """"
    
#     """

def is_typing_list_or_tuple(input_type: typing.Any) -> bool:
    """
    Checks if the given type is a typing.List or typing.Tuple.

    Args:
        input_type (typing.Any): Type to check.

    Returns:
        bool: True if the given type is a typing.List or typing.Tuple, False otherwise.
    """
    return hasattr(input_type, "__origin__") and (input_type.__origin__ == list or input_type.__origin__ == tuple)

def list_contains_any_submodel_element_collections(input_type: typing.Union[typing.List, typing.Tuple]) -> bool:
    return any(issubclass(input_type.__origin__, base.SubmodelElementCollection) for nested_types in input_type.__args__)


def rework_default_list_to_default_factory(model: BaseModel):
    for field in model.__fields__.values():
        if field.default: 
            pass
        if isinstance(field.default, list) or isinstance(field.default, tuple) or isinstance(field.default, set):
            field.type_ = type(field.default[0])
            field.outer_type_ = typing.List[type(field.default[0])]
            field.default = None
            field.field_info = FieldInfo(extra={})
            field.required = True
        if isinstance(field.default, BaseModel):
            field.default = None
            field.field_info = FieldInfo(extra={})
            field.required = True

def create_graphe_pydantic_output_type_for_submodel_elements(
    model: BaseModel,
):
    """
    Create recursively graphene pydantic output types for submodels and submodel elements.

    Args:
        model (typing.Union[base.Submodel, base.SubmodelElementCollectiontuple, list, set, ]): Submodel element for which the graphene pydantic output types should be created.
    """
    for attribute_name, attribute_value in get_all_submodel_elements_from_submodel(model).items():
        # TODO: also check for union types, and resolve their types to graphene pydantic objects
        if hasattr(attribute_value, "__fields__") and issubclass(attribute_value, base.SubmodelElementCollection):
            create_graphe_pydantic_output_type_for_submodel_elements(attribute_value)
        elif is_typing_list_or_tuple(attribute_value):
            if list_contains_any_submodel_element_collections(attribute_value):
                for nested_type in attribute_value.__args__:
                    if issubclass(nested_type, base.SubmodelElementCollection):
                        create_graphe_pydantic_output_type_for_submodel_elements(nested_type)
    create_graphe_pydantic_output_type_for_model(model)

def get_base_query_and_mutation_classes() -> typing.Tuple[graphene.ObjectType, graphene.ObjectType]:
    """
    Returns the base query and mutation classes for the GraphQL endpoint.

    Returns:
        tuple: Tuple of the base query and mutation classes for the GraphQL endpoint.
    """
    class Query(graphene.ObjectType):
        pass
    class Mutation(graphene.ObjectType):
        pass
    return Query, Mutation

def generate_graphql_endpoint(models: List[Type[BaseModel]]) -> GraphQLApp:
    """
    Generates a GraphQL endpoint for the given pydantic models.
    Args:
        models (List[Type[BaseModel]]): List of pydantic models.
    Returns:
        APIRouter: FastAPI router with GraphQL endpoint for the given pydantic models.
    """
    query, mutation = get_base_query_and_mutation_classes()
    # TODO: also make mutation possible
    for model in models:
        model_name = model.__name__
        # model_type = create_model(__model_name=model_name, **base.AAS.__annotations__)
        # FIXME: make it work so that it works with multiple models! Currently the query is overwritten!
        
        submodels = get_all_submodels_from_model(model)
        for submodel in submodels:
            create_graphe_pydantic_output_type_for_submodel_elements(submodel)  

        graphene_model = create_graphe_pydantic_output_type_for_model(model)
        class ModelQuery(query):
            list_models = graphene.List(graphene_model)
            # get_model = graphene.ObjectType(graphene_model)

            async def resolve_list_models(self, info):
                await check_aas_and_sm_server_online()
                data_retrieved = await get_all_aas_from_server(model)
                return data_retrieved
            
            # async def resolve_get_model(self, id_: str, info):
            #     await check_aas_and_sm_server_online()
            #     data_retrieved = await get_aas_from_server(aas_id=id_)
            #     return data_retrieved

        query = ModelQuery
   
    schema = graphene.Schema(query=query)
    return GraphQLApp(schema=schema, on_get=make_graphiql_handler())
