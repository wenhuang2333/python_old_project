from flask import requests
import uuid

from werkzeug.datastructures import Authorization
# for i in range(6):
#     uid=uuid.uuid4()
#     print(uid)
res=requests.post(
    url='http://127.0.0.1:5000',
    json={
        "ordered_string":"ILOVEU",#发送请求

    },
    params={
        "token":"610b7c69-4e76-4510-8886-10c4f631adf3"
    }
)
print(res.json())