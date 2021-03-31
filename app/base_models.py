from abc import ABC, abstractmethod
from string import ascii_lowercase, ascii_uppercase, digits
from random import choice

class AbstractUser(ABC):
    pass

class AbstractItem(ABC):
    pass


class ResponseResult:
    def __init__(self, status_number: int, response_obj: dict):
        self._status = status_number
        self._response_obj = response_obj

    @property
    def response_obj(self):
        return self._response_obj

    @property
    def status(self):
        return self._status

    @property
    def is_ok(self):
        return self._status == 200


class ReferenceToTransfer:
    def __init__(self, sender, receiver, item_to_move, reference=None):
        if reference is None:
            self.reference = self._generate_ref()
        else:
            self.reference = reference
        self.item_to_move = item_to_move
        self.sender = sender
        self.receiver = receiver
        self.response_status: ResponseResult = ResponseResult(500, {'status': 'failed',
                                                                    'reason': 'empty ReferenceToTransfer'})

    def _generate_ref(self):
        letters = ascii_lowercase + ascii_uppercase + digits
        random_token = ''.join(choice(letters) for _ in range(80))
        return random_token



class MovableToAnotherUserInterface(ABC):
    @abstractmethod
    async def create_reference_to_move(self, user_receiver_id: int) -> ReferenceToTransfer:
        pass

    @abstractmethod
    async def move_to_user(self, reference: ReferenceToTransfer) -> ResponseResult:
        pass



