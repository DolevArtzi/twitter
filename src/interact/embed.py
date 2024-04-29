import os
from dotenv import load_dotenv
from transformers import AutoModel
from numpy.linalg import norm
import re
class Embed:
    def __init__(self) -> None:
        load_dotenv()

        self.model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-en', trust_remote_code=True)

    def __call__(self, data):
        return self.model.encode(data,max_length=350)
        


    def clean(text):
        pattern = re.compile(r'[^a-zA-Z\s]')
        return re.sub(pattern, '', text)