from openai import OpenAI
from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass
class LLM_Base_Config:
    base_url: str = ""
    api_key: str = ""


class LLM_Config:
    def __init__(self, model_name):
        self.model_name = model_name
        self.base_config = LLM_Base_Config()
        load_dotenv()
        self._set_base_config()

    def _set_base_config(self):
        try:
            if self.model_name in {"gpt-4o", "gpt-4"}:
                self.base_config.base_url = "https://api.openai.com/v1/"
                self.base_config.api_key = os.getenv("OPENAI_API_KEY")
            elif self.model_name in {'qwen-max', 'qwen-plus', 'qwen_2.5'}:
                self.base_config.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                self.base_config.api_key = os.getenv("QWEN_API_KEY")
        except Exception as e:
            print(e)
            raise