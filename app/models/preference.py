from pydantic import BaseModel

class PreferenceList(BaseModel):
  name:str
  type:str


class PreferencesModel(BaseModel):
  preferences:list[PreferenceList]