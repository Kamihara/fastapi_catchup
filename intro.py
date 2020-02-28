from datetime import datetime
from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import Query
from fastapi import Path
from fastapi import Body
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED
from time import sleep
from typing import Optional, List


app = FastAPI()


def time_bomb(count: int):
    sleep(count)
    print(f"bomb!!! {datetime.utcnow()}")


class Data(BaseModel):
    """request data用の型ヒントがされたクラス"""
    string: str
    default_none: Optional[str] = None
    lists: List[int]

class subDict(BaseModel):
    strings: str
    integer: int

class NestedData(BaseModel):
    subData: subDict
    subDataList: List[subDict]

class ValidatedSubData(BaseModel):
    strings: str = Field(None, min_length=2, max_length=5, regex=r'[a-c]+.')
    integer: int = Field(..., gt=1, le=3)

class ValidatedNestedData(BaseModel):
    subData: ValidatedSubData = Field(..., example={"strings": "aaa", "integer": 2})
    subDataList: List[ValidatedSubData] = Field(...)

class ItemOut(BaseModel):
    strings: str
    aux: int = 1
    text: str


# @app.get('/')
# async def hello():
#     return {'text': 'hello, world!'}

@app.get('/get/{path}')
async def path_and_query_param(
        path: str,
        query: int,
        default_none: str = None):
    return {
        "text": f"hello, {path}, {query}, {default_none}"
    }

@app.get('/validation/{path}')
async def validation(
        string: str = Query(None, min_length=2, max_length=5, regex=r'[a-c]+.'),
        integer: int = Query(..., ge=1, le=3),
        alias: str = Query('default', alias='test'),
        path: int = Path(10)): # pathは自動的にrequiredとなる
    return {
        "string": string,
        "integer": integer,
        "alias_query": alias,
        "path": path
    }

@app.get('/', response_model=ItemOut)
async def response(strings: str, integer: int):
    return {
        "text": "hello, world",
        "strings": strings,
        "integer": integer
    }

# 辞書に存在しない場合、response_modelのattributesのデフォルト値を入れない
@app.get('/unset', response_model=ItemOut, response_model_exclude_unset=True)
async def response_exclude_unset(strings: str, integer: int):
    return {
        "text": "hello world",
        "strings": strings,
        "integer": integer
    }

# response_modelの"strings", "aux"を無視 -> "text"のみ返す
@app.get('/exclude', response_model=ItemOut, response_model_exclude={"strings", "aux"})
async def response_exclude(string: str, integer: int):
    return {
        "text": "hello world",
        "strings": string,
        "integer": integer
    }

# response_modelの"text"のみ考慮する -> "text"のみ返す
@app.get('/include', response_model=ItemOut, response_model_include={"text"})
async def response_include(string: str, integer: int):
    return {
        "text": "hello world",
        "strings": string,
        "integer": integer
    }

@app.get('/status', status_code=200)
async def response_status_code(integer: int, response: Response):
    if integer > 5:
        raise HTTPException(status_code=404, detail="this is error messages")
    elif integer == 1:
        response.status_code = HTTP_201_CREATED
        return {"text": "hello world, created"}
    else:
        return {"text": "hello world"}

@app.get('/{count}')
async def back(count: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(time_bomb, count)
    return {"text": "finished"}

####

@app.post('/post')
async def declare_request_body(data: Data):
    return {
        "text": f"hello, {data.string}, {data.default_none}, {data.lists}"
    }

@app.post('/post/embed')
async def declare_embed_request_body(data: Data = Body(..., embed=True)):
    return {
        "text": f"hello, {data.string}, {data.default_none}, {data.lists}"
    }

@app.post('/post/nested')
async def declare_nested_request_body(data: NestedData):
    return {
        "text": f"hello, {data.subData}, {data.subDataList}"
    }

@app.post('/validation')
async def validation(data: ValidatedNestedData):
    return {
        "text": f"hello, {data.subData}, {data.subDataList}"
    }

