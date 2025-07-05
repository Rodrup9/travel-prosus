from pydantic import BaseModel

class PreferenceList(BaseModel):
  name:str
  type:str


class PreferencesModel(BaseModel):
  user_id:str
  name_user:str
  preferences:list[PreferenceList]