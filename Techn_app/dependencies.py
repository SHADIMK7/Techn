import uuid


def generate_book_code(self):
        code =  f'Ab{uuid.uuid4().hex[:6]}'[:10]
        # print("code is ",code)
        return code