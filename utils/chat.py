import yaml
from pathlib import Path
from openai import OpenAI
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LLM_Config
from functools import lru_cache

@lru_cache
def get_instruction(task_name):
    if not isinstance(task_name, str):
        raise ValueError("task_name must be a string")

    current_path = Path(__file__).resolve().parent  # 绝对路径
    try:
        # 从yaml文件中读取instruction
        # with open(current_path/"instruction.yaml", "r") as f:
        #     instruction = yaml.safe_load(f)
        with open("instruction.yaml", "r", encoding='utf-8') as f:
            instruction = yaml.safe_load(f)

        if task_name not in instruction:
            raise ValueError(f"task_name:{task_name} not in instruction.yaml")
        
        return instruction[task_name]
    except Exception as e:
        raise Exception(f"获取instruction失败:{e}")




async def generate_chat_completion(prompt, task_name, model):
    """
    通过 model名称选用不同api,task_name选用不同instruction 进行推理
    
    :param prompt: 用户输入的对话
    :param task_name: 任务名称
    :param model: 模型名称
    
    :return: API返回的内容

    """
    try:
        config = LLM_Config(model)
        client = OpenAI(
            base_url=config.base_config.base_url,
            api_key=config.base_config.api_key
        )
        instruction = get_instruction(task_name)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': prompt}
            ],
            response_format={"type": "json_object"},

        )

        content = response.choices[0].message.content
        output_token = response.usage.completion_tokens
        input_token = response.usage.prompt_tokens
        return content, input_token, output_token

        # return response.choices[0].message.content

    except Exception as e:
        print(f"生成对话失败:{e}")
        return '{"service_type": "error"}', 0, 0
    


async def test():
    print(await generate_chat_completion("你好", "test", "qwen-max"))

if __name__ == '__main__':
    print("Prompt:")
    print(get_instruction("test"))
    asyncio.run(test())
