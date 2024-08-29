from pydantic import BaseModel

class CodeItem(BaseModel):
    name: str = 'Max'
    body: str = '''if x < y {
  return y;
} else {
  return x;
}
'''

class RunSpec(BaseModel):
    name: str
    argv: tuple = ()
    argd: dict = {}
