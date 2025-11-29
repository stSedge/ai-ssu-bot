class MessageNotFound(Exception):
    def __init__(self, _id: str):
        self._id = _id
        super().__init__(f"Сообщения для сессии с id {_id} не найдены")
