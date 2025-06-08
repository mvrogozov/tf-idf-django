from tf_idf_api_client import AuthenticatedClient
from tf_idf_api_client.models import DocumentList
from tf_idf_api_client.api.v1 import v1_documents_list
from tf_idf_api_client.types import Response


token = None  # ENTER YOUR JWT ACCESS TOKEN HERE
url = 'http://127.0.0.1/'
client = AuthenticatedClient(base_url=url,
                             token=token)

with client:
    data: DocumentList = v1_documents_list.sync(client=client)
    response: Response[DocumentList] = v1_documents_list.sync_detailed(
        client=client
    )

print(f'DATA >> {data}\nRESPONSE >> {response}')
