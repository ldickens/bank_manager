from enum import Enum, auto


class UIUpdateReason(Enum):
    UPDATE_MEDIA_SHEET = auto()
    UPDATE_BANK_SHEET = auto()
    UPDATE_IMPORT_SHEET = auto()
    UPDATE_STATUS = auto()
    UI_STATE = auto()
    DISCONNECT = auto()
    VERIFY_IMPORT_SHEET = auto()
    CREATE_UPLOAD_PROGRESS_BAR = auto()
    SET_WORKING_BAR = auto()
