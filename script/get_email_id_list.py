from typing import List

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_service_processor import get_email_service_data_from_db


def get_first_email_id_of_each_service(service_id_list: List[str]):
    """
    通过邮件服务单号在数据库中查询所有对应的第一封邮件id"""
    email_id_list = []

    batch_size = 500
    for i in range(0, len(service_id_list), batch_size):
        batch = service_id_list[i:i+batch_size]
        email_service_data_list = get_email_service_data_from_db(batch)
        for email_service_data in email_service_data_list:
            email_list = email_service_data.get("email_list", [])
            if email_list:
                email_id_list.append(email_list[0]["email_id"])
            # email_id_list.extend([email["email_id"] for email in email_list])

    return email_id_list


def main():
    service_id_file = "email_service_ids.txt"
    with open(service_id_file, "r") as f:
        service_id_list = [line.strip() for line in f.readlines()]

    email_id_list = get_first_email_id_of_each_service(service_id_list)
    with open('email_ids.txt', 'w') as f:
        for email_id in email_id_list:
            f.write(f"{email_id}\n")


if __name__ == '__main__':
    main()
