class AppState:
    connected: bool = bool(False)
    update_media: bool = bool(False)
    update_system: bool = bool(False)

    uploading: bool = False
    progress_steps: int = 0
    total_steps: int = 0

    @staticmethod
    def reset_uploading() -> None:
        AppState.uploading = False
        AppState.progress_steps = 0
        AppState.total_steps = 0
