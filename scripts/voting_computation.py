from fastapi import APIRouter

from pydantic import BaseModel
import base64

from lib.crypto import decrypt_aes

router = APIRouter()

_KEYS = {}
_DATA = {}

class KeyItem(BaseModel):
    key: str
    userid: str

class DataItem(BaseModel):
    value: str
    iv: str
    userid: str
    
@router.post("/key")
async def add_key(keyitem:KeyItem):
    key = base64.b64decode(keyitem.key)
    uid = str(keyitem.userid)
    _KEYS[uid]=key
    print("Stored new key for user", uid)

@router.post("/data")
async def add_data(items: list[DataItem]):
    for item in items:
        encrypted = base64.b64decode(item.value)
        iv = base64.b64decode(item.iv)
        userid=item.userid

        raw=decrypt_aes(encrypted, _KEYS[userid], iv)
        _DATA[userid]=raw
        print(f"Adding data:\'{raw}\' for user", userid)

@router.get("/result")
async def get_result():
    from functions import verified_voting
    array=[int(d) for d in _DATA.values()]

    count, value = verified_voting(array)
    print("Winner:", value,"with votes:", count)
    # print("Counts:", count,"Value:", value)
    return {'value':value, 'votes':count}
