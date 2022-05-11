from openai import api_requestor, util, error
from openai.api_resources.abstract.api_resource import APIResource
from openai.util import ApiType


class ListableAPIResource(APIResource):
    @classmethod
    def auto_paging_iter(cls, *args, **params):
        return cls.list(*args, **params).auto_paging_iter()

    @classmethod
    def list(
        cls,
        api_key=None,
        request_id=None,
        api_version=None,
        organization=None,
        api_base=None,
        api_type=None,
        **params,
    ):
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=api_base or cls.api_base(),
            api_version=api_version,
            api_type=api_type,
            organization=organization,
        )

        typed_api_type, api_version = cls._get_api_type_and_version(api_type, api_version)

        if typed_api_type == ApiType.AZURE:
            base = cls.class_url()
            url = f"/{cls.azure_api_prefix}{base}?api-version={api_version}"
        elif typed_api_type == ApiType.OPEN_AI:
            url = cls.class_url()
        else:
            raise error.InvalidAPIType(f'Unsupported API type {api_type}')            

        response, _, api_key = requestor.request(
            "get", url, params, request_id=request_id
        )
        openai_object = util.convert_to_openai_object(
            response, api_key, api_version, organization
        )
        openai_object._retrieve_params = params
        return openai_object
