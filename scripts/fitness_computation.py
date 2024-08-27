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

@router.get("/hello", tags=["fitness"])
async def hello():
    return "Hello from Fitness congestion service"

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

@router.get("/median")
async def get_median():
    print("Should compute median value of data:")
    from functions import verified_sort
    values = []
    for userid,value in _DATA.items():
        values.append(int(value))
    print("Unsorted:", values)
    sorted = verified_sort(values)
    print("Sorted:", sorted)
    median = -1
    i = len(sorted)//2
    print("len/2:", i)
    if len(sorted)%2==0:
        print("Is even, take mean")
        median = (sorted[i-1]+sorted[i])/2 
    else:
        print("In not even, take middle")
        median = sorted[i+1]
    print("Computed median:", median)
    return median
    # zone_count = []
    # for userid, value in _DATA.items():
    #     # print("userid:", userid, 'value:', value)
    #     zone_count.append(int(value))
    # print("Zone count:", zone_count)
    # res = verified_count(zone_id, zone_count)
    # print("Result:", res)
    # return res
