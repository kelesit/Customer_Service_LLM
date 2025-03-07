"""
验证使用llm生成客服回复的工作流
核心组件：
服务单数据获取
服务单数据处理
判断器
回复生成器

目前只处理售中-物流咨询的问题

author: hsy
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
from functools import lru_cache
from pathlib import Path
import json
import pandas as pd
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from email_service_processor import get_email_service_data_from_db
from email_processor import get_email_data_with_api, get_single_email_data_with_api
from data_structure.email_service import Email_Service
from utils.tools import get_email_content

import yaml


load_dotenv()
client = OpenAI(
    # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # api_key=os.getenv("QWEN_API_KEY")
    base_url = "https://api.openai.com/v1/",
    api_key=os.getenv("OPENAI_API_KEY")
)

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



def load_configs():
    with open('D:/work/email_anay/configs.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
    

# 物流信息
class ShippingInfo(BaseModel):
    tracking_number: str  # 物流跟踪号
    carrier: str  # 承运商/物流公司
    shipping_status: str  # 物流状态
    current_location: Optional[str] = None  # 当前位置
    estimated_delivery_time: Optional[str] = None  # 预计送达时间
    shipping_date: Optional[str] = None  # 发货日期
    last_update: Optional[str] = None  # 最后更新时间
    tracking_url: Optional[str] = None  # 物流查询网址
    # shipping_events: Optional[List[dict]] = None  # 物流事件/轨迹


class CustomerInfo(BaseModel):
    pass

class OrderInfo(BaseModel):
    # 订单基本信息
    order_id: Optional[str] = None  # 短订单号（顾客可见的订单号）
    real_order_id: Optional[str] = None   # 订单号
    order_time: Optional[str] = None  # 下单时间
    order_website: Optional[str] = None  # 来源网站
    pay_method: Optional[str] = None  # 支付方式
    shipping_method: Optional[str] = None    # 物流方式

    # 状态/时间类信息
    order_status: Optional[str] = None   # 订单状态
    shipping_status: Optional[str] = None    # 物流状态
    estimated_delivery_time: Optional[str] = None   # 预计送达时间
    fund_status: Optional[str] = None    # 资金状态


class Email(BaseModel):
    email_id: str
    subject: str
    content: str
    time: str



# 定义回复级别枚举
class ReplyLevel(int, Enum):
    HUMAN_SERVICE = 1  # 人工客服
    LLM_HUMAN_SERVICE = 2  # LLM+人工客服
    LLM_AUTO = 3  # LLM+系统自动处理

# 定义服务单类型枚举
class ServiceType(str, Enum):
    INFO_CONSULT = "信息咨询类"  # 信息咨询类
    BUSINESS_PROCESS = "业务办理类"  # 业务办理类
    OTHER = "其他类"  # 其他类


# 定义服务单所处阶段枚举
class ServiceStage(str, Enum):
    QUESTION_CONFIRM = "问题确认"  # 问题确认阶段
    COMMUNICATION = "沟通协商"  # 沟通协商阶段
    SYSTEM_OPERATION = "系统操作"  # 系统操作阶段
    OTHER = "其他类"  # 其他类


class LLM_Response(BaseModel):
    reply: Optional[str] = None  # LLM生成的回复内容
    reply_level: ReplyLevel  # 回复级别
    service_type: ServiceType  # 服务单类型
    service_stage: ServiceStage  # 服务单所处阶段
    # need_human_intervention: bool = False   # 是否需要转人工处理
    intervention_reson: Optional[str] = None    # 需要转人工的原因
    analysis_summary: Optional[str] = None  # LLM分析的摘要
    cost: Optional[float] = None  # LLM计算的成本


class Service(BaseModel):
    service_id: str
    latest_customer_emails: List[Email]   # 最新的顾客邮件
    latest_service_emails: List[Email]     # 最新的客服邮件

    # 订单和物流信息
    order_info: Optional[OrderInfo] = None
    shipping_info: Optional[ShippingInfo] = None

    # LLM分析结果
    llm_response: Optional[LLM_Response] = None


def get_latest_customer_emails(email_list: List[dict]) -> List[Email]:
    """
    获取最新的顾客邮件
    最新的type为1的邮件到最新的type为2的邮件之间的邮件
    """
    latest_customer_email_ids = []
    for email in email_list:
        if email['email_type'] != '1':
            continue
        if email['email_type'] == '1':
            latest_customer_email_ids.append(email['email_id'])
        if email['email_type'] == '2':
            break

    latest_customer_emails = []
    for email_id in latest_customer_email_ids:
        email_data = get_single_email_data_with_api(email_id)
        if not email_data:
            email = Email(email_id=email_id, content='邮件内容获取失败')
            latest_customer_emails.append(email)
        else:
            content = get_email_content(email_data['content'])
            time = email_data['time']
            subject = email_data['subject']
            email = Email(email_id=email_id, subject=subject, content=content, time=time)
            latest_customer_emails.append(email)
        
    return latest_customer_emails
    

def get_latest_service_emails(email_list: List[dict]) -> List[dict]:
    """
    获取最新的客服邮件
    最新的type为2的邮件到最新的type为1的邮件之间的邮件
    """
    latest_service_email_ids = []
    for email in email_list:
        if email['email_type'] != '2':
            continue
        if email['email_type'] == '2':
            latest_service_email_ids.append(email['email_id'])
        if email['email_type'] == '1':
            break

    latest_service_emails = []
    for email_id in latest_service_email_ids:
        email_data = get_single_email_data_with_api(email_id)
        if not email_data:
            email = Email(email_id=email_id, content='邮件内容获取失败')
            latest_service_emails.append(email)
        else:
            content = get_email_content(email_data['content'])
            time = email_data['time']
            subject = email_data['subject']
            email = Email(email_id=email_id, subject=subject, content=content, time=time)
            latest_service_emails.append(email)
    return latest_service_emails


def get_latest_type_emails(email_list: List[dict], email_type: str) -> List[Email]:
    """获取最新的type为email_type的邮件"""
    if email_type not in ['1', '2']:
        raise ValueError('email_type must be 1 or 2')
    if email_type == '1':
        opposite_type = '2'
    else:
        opposite_type = '1'

    latest_email_ids = []
    # 首先找到email_type为email_type的邮件idx
    idx = 0
    for email in email_list:
        if email['email_type'] == email_type:
            break
        idx += 1

    # 从idx开始找到email_type为opposite_type的之间邮件
    for email in email_list[idx:]:
        if email['email_type'] == email_type:
            latest_email_ids.append(email['email_id'])
        if email['email_type'] == opposite_type:
            break

    latest_emails = []
    for email_id in latest_email_ids:
        email_data = get_single_email_data_with_api(email_id)
        if not email_data:
            email = Email(email_id=email_id, subject="", time="", content='邮件内容获取失败')
            latest_emails.append(email)
        else:
            content = get_email_content(email_data['content'])
            time = email_data['time']
            subject = email_data['subject']
            email = Email(email_id=email_id,subject=subject, content=content, time=time)
            latest_emails.append(email)
    return latest_emails


def get_order_info(order_id):
    """获取订单信息的外部api"""
    # 模拟生成订单信息
    real_order_id = order_id
    order_time = datetime.now() - timedelta(days=20)
    order_info = OrderInfo(
        order_id=order_id,
        real_order_id=real_order_id,
        order_time=order_time.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化为字符串
        order_website="litfad.com",
        pay_method="Paypal",
        shipping_method="标准配送",
        order_status="已发货",
        shipping_status="运输中",
        estimated_delivery_time=(datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),  # 预计45天后送达
        fund_status="已支付"
    )
    return order_info


def get_tracking_url(carrier, tracking_number):
    configs = load_configs()
    tracking_urls = configs.get('tracking_url', {})
    
    # 获取承运商的URL模板，如果没有找到则使用默认模板
    url_template = tracking_urls.get(carrier, tracking_urls.get('default', ''))
    
    # 将物流单号插入到URL模板中
    if url_template:
        return url_template.format(tracking_number=tracking_number)
    return None


def get_shipping_info(order_id):
    """获取物流信息的外部api"""
    # 模拟生成物流信息
    now = datetime.now()
    tracking_number = f'tracking_number_{order_id}'
    carriers = ['DHL', 'FedEx', 'UPS', 'USPS', 'EMS', 'default']
    # 随机模拟一个物流公司
    carrier = random.choice(carriers)
    tracking_url = get_tracking_url(carrier, tracking_number)
    shipping_info = ShippingInfo(
        tracking_number=tracking_number,  # 用订单号模拟物流追踪号
        carrier=carrier,
        shipping_status="运输中",
        current_location="上海物流中心",
        estimated_delivery_time=(datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),  # 预计45天后送达
        shipping_date=(now - timedelta(days=19)).strftime("%Y-%m-%d"),
        last_update=(now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
        tracking_url=tracking_url
    )
    return shipping_info


def get_service(email_service_data: dict) -> Service:
    """
    通过服务单号从api获取服务单数据
    包括服务单的最新邮件内容，服务单号，顾客姓名，订单号，包裹号等等
    """
    email_list = email_service_data['email_list'] 

    # 获取邮件内容
    latest_customer_emails = get_latest_type_emails(email_list, '1')
    latest_service_emails = get_latest_type_emails(email_list, '2')

    # 获取订单信息
    order_id = email_service_data['email_service_id']   # 先用服务单号模拟订单号
    order_info = get_order_info(order_id)
    shipping_info = get_shipping_info(order_id)

    service = Service(
        service_id=email_service_data['email_service_id'],
        latest_customer_emails=latest_customer_emails,
        latest_service_emails=latest_service_emails,
        order_info=order_info,
        shipping_info=shipping_info
    )

    return service


def llm_service_analysis(service, combined_content: str) -> ServiceType:
    """
    使用LLM根据邮件内容判断服务单类型
    1. 信息咨询类
    2. 业务办理类
    3. 其他类
    """
    instruction = get_instruction('service_analysis')
    response = client.chat.completions.create(
            # model='qwen-max',
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': combined_content}
            ],
            response_format={"type": "json_object"},

        )

    content = response.choices[0].message.content
    output_token = response.usage.completion_tokens
    input_token = response.usage.prompt_tokens
    cost = (input_token*0.0024 + output_token*0.0096)/1000
    try:
        result = json.loads(content)
        service.llm_response = LLM_Response(
            reply=result.get('reply', ''),
            reply_level=ReplyLevel(result.get('reply_level', 1)),  # 默认人工客服
            service_type=ServiceType(result.get('service_type', 3)),    # 默认其他类
            service_stage=ServiceStage(result.get('service_stage', 4)), # 默认其他
            analysis_summary=result.get('analysis_summary', ''),
            intervention_reson=result.get('intervention_reson', ''),
            cost=cost
        )
    except Exception as e:
        print(f"LLM分析服务单类型失败:{e}")
        service.llm_response = LLM_Response(
            reply="LLM分析失败,请转人工处理",
            reply_level=ReplyLevel.HUMAN_SERVICE,
            service_type=ServiceType.OTHER,
            service_stage=ServiceStage.OTHER,
            analysis_summary="",
            intervention_reson="LLM分析失败",
            cost=cost
        )
    return service

def info_consult_analysis(service: Service) -> Service:
    """分析服务单数据可否支持信息咨询类回复"""
    instruction = get_instruction('info_consult_analysis')
    # 构建LLM输入
    # input_content = json.dumps(service.model_dump(exclude={'latest_service_emails'}))
    service_info = service.model_dump(exclude={'latest_service_emails', 'latest_customer_emails', 'llm_response'})
    email_content = [email.content for email in service.latest_customer_emails]
    combined_email_content = '\n'.join(email_content)
    input_content = json.dumps({
        'service_info': service_info,
        'email_content': combined_email_content
    }, ensure_ascii=False)
    response = client.chat.completions.create(
            # model='qwen-max',
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': input_content}
            ],
            response_format={"type": "json_object"},

        )

    content = response.choices[0].message.content
    output_token = response.usage.completion_tokens
    input_token = response.usage.prompt_tokens
    cost = service.llm_response.cost+(input_token*0.0024 + output_token*0.0096)/1000
    try:
        result = json.loads(content)
        """
        {
            "info_check": "信息不全",
            "info_need": "顾客需要说明书" # 如果信息不全，需要说明顾客需要的信息
        }
        {
            "info_check": "信息充足"
            "info_need": "" # 如果信息充足，不需要填写
        }"""
        if result.get('info_check') == "信息不全":
            service.llm_response = LLM_Response(
                reply="",
                reply_level=ReplyLevel.HUMAN_SERVICE,
                service_type=ServiceType.INFO_CONSULT,
                service_stage=ServiceStage.QUESTION_CONFIRM,
                intervention_reson=result.get('info_need', ''),
                cost=cost
            )
        elif result.get('info_check') == "信息充足":
            service.llm_response = LLM_Response(
                reply="",
                reply_level=ReplyLevel.LLM_HUMAN_SERVICE,   # LLM+人工客服
                service_type=ServiceType.INFO_CONSULT,
                service_stage=ServiceStage.QUESTION_CONFIRM,
                intervention_reson="",
                cost=cost
            )
        else:
            service.llm_response = LLM_Response(
                reply="",
                reply_level=ReplyLevel.HUMAN_SERVICE,
                service_type=ServiceType.INFO_CONSULT,
                service_stage=ServiceStage.QUESTION_CONFIRM,
                intervention_reson="LLM分析失败",
                cost=cost
            )
    except Exception as e:
        print(f"LLM分析信息咨询类失败:{e}")
        service.llm_response = LLM_Response(
            reply="LLM分析失败,请转人工处理",
            reply_level=ReplyLevel.HUMAN_SERVICE,
            service_type=ServiceType.INFO_CONSULT,
            service_stage=ServiceStage.QUESTION_CONFIRM,
            intervention_reson="LLM分析失败",
            cost=cost
        )
    return service


def business_process_analysis(service: Service) -> Service:
    #TODO
    return service


def service_context_analysis_llm(service: Service) -> Service:
    """
    使用LLM对服务单进行上下文分析
    一、判断服务单类型：信息咨询类 or 业务办理类 or 其他类
    二、判断所处阶段：问题确认阶段 or 协商沟通阶段 or 系统操作阶段
    三、根据服务单类型和所处阶段，确认回复级别
    class ReplyLevel(int, Enum):
        HUMAN_SERVICE = 1  # 人工客服
        LLM_HUMAN_SERVICE = 2  # LLM+人工客服
        LLM_AUTO = 3  # LLM+系统自动处理
    """

    # 1. 服务单合法性判断
    if not service.latest_customer_emails:
        service.llm_response = LLM_Response(
            reply_level=ReplyLevel.HUMAN_SERVICE,
            service_type=ServiceType.OTHER,
            service_stage=ServiceStage.OTHER,
            intervention_reson="无顾客邮件"
        )
        return service
    
    customer_emails_content = [email.content for email in service.latest_customer_emails]
    combined_content = '\n'.join(customer_emails_content)

    # 使用LLM判断服务单类型和所处阶段
    service = llm_service_analysis(service, combined_content)
    
    # 进一步分析
    if service.llm_response.service_type == ServiceType.INFO_CONSULT:
        service = info_consult_analysis(service)
        return service
    elif service.llm_response.service_type == ServiceType.BUSINESS_PROCESS:
        service = business_process_analysis(service)
        return service  # 尚未实现
    else:   # 其他类
        return service # 其他类不做进一步处理, 因为回复类型默认是人工客服


def reply_generator(service: Service, max_retries: int = 3, backoff_factor: float = 1.5) -> Service:
    """让LLM生成回复"""
    if not service.llm_response:
        return service
    
    if service.llm_response.reply_level == ReplyLevel.HUMAN_SERVICE:
        return service
    
    if service.llm_response.service_type == ServiceType.INFO_CONSULT:
        instruction = get_instruction('info_consult_reply')

    input_content = json.dumps(service.model_dump(exclude={'latest_service_emails'}))

    additional_cost = 0
    retry_count = 0
    while retry_count <= max_retries:
        try:
            response = client.chat.completions.create(
                    # model='qwen-max',
                    model='gpt-4o',
                    messages=[
                        {'role': 'system', 'content': instruction},
                        {'role': 'user', 'content': input_content}
                    ],
                    response_format={"type": "json_object"},
                )
        
            content = response.choices[0].message.content
            output_token = response.usage.completion_tokens
            input_token = response.usage.prompt_tokens
            current_cost = (input_token*0.0024 + output_token*0.0096)/1000
            additional_cost += current_cost

            try:
                result = json.loads(content)
                reply = result.get('reply', '')
                service.llm_response.reply = reply
                service.llm_response.cost = (service.llm_response.cost or 0) + additional_cost
                return service
            except json.JSONDecodeError as json_err:
                print(f"LLM返回的内容不是有效的JSON格式: {json_err}")
                if retry_count == max_retries:
                    raise  # 如果是最后一次尝试，重新抛出异常
            except ValueError as val_err:
                print(f"LLM返回的内容验证失败: {val_err}")
                if retry_count == max_retries:
                    raise  # 如果是最后一次尝试，重新抛出异常
        except Exception as e:
            print(f"尝试 {retry_count + 1}/{max_retries + 1} 失败: {e}")
            if retry_count == max_retries:
                print(f"LLM生成回复失败，已达最大重试次数{e}")
                service.llm_response.reply = "LLM生成回复失败"
                service.llm_response.cost = (service.llm_response.cost or 0) + additional_cost
                service.llm_response.intervention_reson = f"LLM回复生成失败: {str(e)}"
                return service
        wait_time = backoff_factor ** retry_count
        print(f"等待{wait_time:.2f}秒后重试...")
        time.sleep(wait_time)
        retry_count += 1

    service.llm_response.reply = "LLM生成回复失败，请转人工处理"
    service.llm_response.cost = (service.llm_response.cost or 0) + additional_cost
    return service


def process_service(email_service: Email_Service):
    """模拟当该服务单传进来时的处理流程"""
    # 1. 获取该服务单信息，构建服务单对象
    service = get_service(email_service)
    # 2. 判断器
    service = service_context_analysis_llm(service)
    print(service.llm_response)
    # 3. 回复生成器
    service = reply_generator(service)
    print(service.llm_response)

    return service



def get_service_id_list(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as f:
        service_id_list = [line.strip() for line in f.readlines()]
    return service_id_list


def main():
    # 1. 服务单数据构建
    service_ids_file = 'D:\work\email_anay\data\email_service_ids_beta.txt'
    service_id_list = get_service_id_list(service_ids_file)
    services_data = get_email_service_data_from_db(service_id_list)

    processed_services = []
    # 2. 服务单数据处理
    for service_data in services_data:
        if service_data:
            processed_service = process_service(service_data)
            processed_services.append(processed_service)



    # 3. 对比结果构建
    result_dicts = []
    result_df = pd.DataFrame(columns=['service_id', 'human_reply', 'llm_reply', 'service_type', 'service_stage', 'reply_level', 'intervention_reson', 'cost'])
    for service in processed_services:
        service_dict = service.model_dump()
        result_dicts.append(service_dict)
        if service.llm_response:
            new_row = pd.DataFrame([{
                'service_id': service.service_id,
                'human_reply': service.latest_service_emails[-1].content if service.latest_service_emails else "",
                'llm_reply': service.llm_response.reply,
                'service_type': service.llm_response.service_type,
                'service_stage': service.llm_response.service_stage,
                'reply_level': service.llm_response.reply_level,
                'intervention_reson': service.llm_response.intervention_reson,
                'cost': service.llm_response.cost
            }])
            result_df = pd.concat([result_df, new_row], ignore_index=True)
    
    result_df.to_csv('D:\work\email_anay\data\llm_reply_result.csv', index=False)
    with open('D:\work\email_anay\data\llm_reply_result.json', 'w', encoding='utf-8') as f:
        json.dump(result_dicts, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    # 1. 服务单数据准备 见notebooks/test.ipynb
    main()
