class AppState:
    _update_media: bool = bool(False)
    _update_system: bool = bool(False)

    _uploading: bool = False
    _progress_steps: int = 0
    _total_steps: int = 0

    @staticmethod
    def reset_uploading() -> None:
        AppState._uploading = False
        AppState._progress_steps = 0
        AppState._total_steps = 0
