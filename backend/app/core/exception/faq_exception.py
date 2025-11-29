class FAQNotFound(Exception):
    def __init__(self, _id: int):
        self._id = _id
        super().__init__(f"FAQ с id {_id} не найден")