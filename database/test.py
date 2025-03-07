from database import get_db, engine, init_db
from models import Base
from crud import EmailServiceCRUD, EmailCRUD
from sqlalchemy import inspect


def test_create_tables():
    # init_db()
    """重建数据库表"""
    inspector = inspect(engine)
    
    # 检查表是否存在
    print("检查数据库表状态...")
    tables = inspector.get_table_names()
    
    if 'email_services' in tables or 'emails' in tables:
        print("删除已存在的表...")
        Base.metadata.drop_all(engine)
        print("旧表删除完成")
    
    print("创建新表...")
    Base.metadata.create_all(engine)
    print("表创建完成")



def test_create_service():
    db = next(get_db())

    service_data = {
        "email_service_id": "6657",
        "customer_address": "test@test.com",
        "email_account_id": "1121",
        "title": "服务单：6657",
        "status": "7",
        "add_time": "2025-02-19 17:33:39",
        "type": "10",
        "email_list": [
            {
                "email_id": "7756",
                "email_type": "1"
            }
        ]
    }

    service = EmailServiceCRUD.create_service(db, service_data)
    print(f"创建服务单成功: {service.title}")
    return service

def test_create_email():
    db = next(get_db())

    email_data = {
            "email_id": "7756",
            "email_type": "1",
            "from_name": "Esra Nur Akbayrak",
            "from_address": "esranurakbayrak@outlook.com",
            "to_name": "Litfad Support",
            "to_address": "support@litfad.com",
            "subject": "Re: Order 979740 Confirmation",
            "content_preview": "Dear Team, Can you kindly confirm when this will be delivered. K",
            "status": "0",
            "is_star": "0",
            "time": "2025-02-19 17:31:10",
            "has_attachment": "0",
            "task_flow": "0",
            "user_id": "0",
            "email_template_id": "0",
            "category_id": "20503",
            "related_email_id": "0",
            "email_account_id": "36311",
            "is_recycle": "0",
            "email_service_id": "6657",
            "email_address_book_id": "0",
            "email_type_id": "0",
            "content": "<html>\r\n<head>\r\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=Windows-1252\">\r\n<style type=\"text/css\" style=\"display:none;\"> P {margin-top:0;margin-bottom:0;} </style>\r\n</head>\r\n<body dir=\"ltr\">\r\n<div class=\"elementToProof\" style=\"font-family: Calibri, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0);\">\r\nDear Team,&nbsp;</div>\r\n<div class=\"elementToProof\" style=\"font-family: Calibri, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0);\">\r\n<br>\r\n</div>\r\n<div class=\"elementToProof\" style=\"font-family: Calibri, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0);\">\r\nCan you kindly confirm when this will be delivered.&nbsp;</div>\r\n<div class=\"elementToProof\" style=\"font-family: Calibri, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0);\">\r\n<br>\r\n</div>\r\n<div class=\"elementToProof\" style=\"font-family: Calibri, Helvetica, sans-serif; font-size: 12pt; color: rgb(0, 0, 0);\">\r\nKind regards&nbsp;</div>\r\n<div id=\"appendonsend\"></div>\r\n<hr style=\"display:inline-block;width:98%\" tabindex=\"-1\">\r\n<div id=\"divRplyFwdMsg\" dir=\"ltr\"><font face=\"Calibri, sans-serif\" style=\"font-size:11pt\" color=\"#000000\"><b>From:</b> Litfad Support &lt;support@litfad.com&gt;<br>\r\n<b>Sent:</b> 16 January 2025 17:48<br>\r\n<b>To:</b> Esra Akbayrak &lt;esranurakbayrak@outlook.com&gt;<br>\r\n<b>Subject:</b> Order 979740 Confirmation</font>\r\n<div>&nbsp;</div>\r\n</div>\r\n<div><style>\r\n<!--\r\n*\r\n\t{margin:0;\r\n\tpadding:0;\r\n\tbox-sizing:border-box}\r\n*:before, *:after\r\n\t{box-sizing:border-box}\r\n#x_content-out\r\n\t{background-color:#F0F0F0}\r\n#x_content-inner\r\n\t{max-width:650px;\r\n\tmargin:0 auto}\r\n.x_message\r\n\t{width:100%;\r\n\tpadding:6%;\r\n\tmargin:0 auto}\r\n.x_content\r\n\t{background-color:#fff;\r\n\twidth:100%;\r\n\tpadding-left:5.2%;\r\n\tpadding-right:5.2%;\r\n\tborder:1px solid #e5e5e5;\r\n\tborder-radius:5px}\r\n.x_content .x_logo\r\n\t{padding-top:25px;\r\n\ttext-align:left}\r\n.x_content .x_logo img\r\n\t{height:35px;\r\n\tmax-width:110px}\r\n.x_content h3.x_title\r\n\t{text-align:left;\r\n\theight:27px;\r\n\tline-height:27px;\r\n\tfont-style:'Open Sans';\r\n\tfont-weight:bold;\r\n\tcolor:#3B2728;\r\n\tfont-size:20px;\r\n\tmargin-top:40px;\r\n\tmargin-bottom:30px}\r\n.x_content p\r\n\t{font-style:'Open Sans';\r\n\ttext-align:left;\r\n\tcolor:#3B2728;\r\n\tfont-size:13px;\r\n\tline-height:22px}\r\n.x_content .x_welcome\r\n\t{margin-bottom:30px}\r\n.x_content .x_address\r\n\t{width:100%;\r\n\tmargin-bottom:30px;\r\n\toverflow:hidden}\r\n.x_content .x_address .x_shipping\r\n\t{float:left}\r\n.x_content .x_address .x_billing\r\n\t{float:right}\r\n.x_content .x_address .x_address-info\r\n\t{width:49%;\r\n\tpadding:3%}\r\n.x_content .x_address .x_address-info h3\r\n\t{font-weight:bold;\r\n\tcolor:#3B2728;\r\n\tfont-size:13px;\r\n\theight:18px;\r\n\tline-height:18px;\r\n\tmargin-bottom:20px}\r\n.x_content .x_link\r\n\t{margin-bottom:14px}\r\n.x_content .x_link span\r\n\t{font-weight:bold}\r\n.x_content .x_link a\r\n\t{color:#f1752d;\r\n\ttext-decoration:underline}\r\n.x_content .x_detail\r\n\t{width:100%;\r\n\tborder-collapse:collapse}\r\n.x_content .x_detail td\r\n\t{border:1px solid #E5E5E5;\r\n\tfont-style:'Open Sans';\r\n\tcolor:#3B2728;\r\n\tfont-size:12px}\r\n.x_content .x_detail .x_line .x_products\r\n\t{width:40%}\r\n.x_content .x_detail .x_line .x_quantity\r\n\t{width:20%}\r\n.x_content .x_detail .x_line .x_sku\r\n\t{width:20%}\r\n.x_content .x_detail .x_line .x_amount\r\n\t{width:20%}\r\n.x_content .x_detail .x_line.title td\r\n\t{height:24px;\r\n\tbackground-color:#F5F5F5;\r\n\tcolor:#3B2728;\r\n\tfont-style:'Open Sans';\r\n\tfont-weight:bold;\r\n\ttext-align:center;\r\n\tfont-size:12px;\r\n\tline-height:24px}\r\n.x_content .x_detail .x_line.title td.x_products\r\n\t{text-align:left;\r\n\tpadding-left:25px}\r\n.x_content .x_detail .x_line.pdt-info .x_products\r\n\t{overflow:hidden}\r\n.x_content .x_detail .x_line.pdt-info .x_products .x_image\r\n\t{float:left;\r\n\twidth:30%;\r\n\tpadding-left:5%;\r\n\tdisplay:table-cell;\r\n\tvertical-align:middle;\r\n\tmargin:18px 0 10px}\r\n.x_content .x_detail .x_line.pdt-info .x_products .x_image img\r\n\t{width:100%}\r\n.x_content .x_detail .x_line.pdt-info .x_products .x_info\r\n\t{width:70%;\r\n\tfloat:left;\r\n\tpadding:10px 5px 10px 10px}\r\n.x_content .x_detail .x_line.pdt-info .x_products .x_info .x_name\r\n\t{font-style:'Open Sans';\r\n\tcolor:#3B2728;\r\n\tfont-size:12px;\r\n\tline-height:16px;\r\n\ttext-decoration:underline;\r\n\tmargin-bottom:5px}\r\n.x_content .x_detail .x_line.pdt-info .x_products .x_info .x_attr\r\n\t{font-style:'Open Sans';\r\n\tcolor:#3B2728;\r\n\tfont-size:12px;\r\n\tline-height:16px}\r\n.x_content .x_detail .x_line.pdt-info .x_quantity, .x_content .x_detail .x_line.pdt-info .x_sku, .x_content .x_detail .x_line.pdt-info .x_amount\r\n\t{text-align:center;\r\n\tvertical-align:middle}\r\n.x_content .x_fee\r\n\t{margin-top:20px;\r\n\tmargin-bottom:30px}\r\n.x_content .x_fee h3\r\n\t{font-style:'Open Sans';\r\n\tfont-weight:bold;\r\n\tcolor:#3B2728;\r\n\tfont-size:13px;\r\n\theight:18px;\r\n\tline-height:18px}\r\n.x_content .x_fee p\r\n\t{margin-top:7px;\r\n\toverflow:hidden}\r\n.x_content .x_fee p .x_title\r\n\t{float:left}\r\n.x_content .x_fee p .x_value\r\n\t{float:right}\r\n.x_content .x_fee p.x_total\r\n\t{border-top:1px solid #E5E5E5;\r\n\tpadding-top:10px}\r\n.x_content .x_fee p.x_total span\r\n\t{font-weight:bold}\r\n.x_content .x_sender\r\n\t{margin-top:30px;\r\n\tpadding-bottom:40px;\r\n\tfont-weight:Bold;\r\n\tcolor:#3B2728;\r\n\tfont-size:12px}\r\n-->\r\n</style>\r\n<div id=\"x_content-out\">\r\n<div id=\"x_content-inner\">\r\n<div class=\"x_message\">\r\n<div class=\"x_content\">\r\n<div class=\"x_logo\"><img src=\"https://res.litfad.net/site/img/logo/main_logo.png\">\r\n</div>\r\n<h3 class=\"x_title\">Dear Esra Akbayrak:</h3>\r\n<p class=\"x_welcome\">Thanks for your order, we hope you had a good time shopping with us. Your order is now being processed, according to your order Order reserved address, we will deliver your merchandise to:\r\n</p>\r\n<div class=\"x_address\">\r\n<div class=\"x_shipping x_address-info\">\r\n<h3>Shipping Address:</h3>\r\n<p>70 Marmion Close , Esra Akbayrak</p>\r\n<p>London, Greater London E4 8EW</p>\r\n<p>United Kingdom</p>\r\n<p>+44 7594516330</p>\r\n</div>\r\n<div class=\"x_billing x_address-info\">\r\n<h3>Billing Address:</h3>\r\n<p>70 Marmion Close , Esra Akbayrak</p>\r\n<p>London, Greater London E4 8EW</p>\r\n<p>United Kingdom</p>\r\n<p>+44 7594516330</p>\r\n</div>\r\n</div>\r\n<p class=\"x_link\">Your order Number is: <span>979740</span> ; You can <a href=\"https://www.litfad.com/orderDetail/index?order_id=979740\">\r\nclick here</a> to view more details.</p>\r\n<table class=\"x_detail\">\r\n<tbody>\r\n<tr class=\"x_line x_title\">\r\n<td class=\"x_products\">Products</td>\r\n<td class=\"x_amount\">Amount</td>\r\n</tr>\r\n<tr class=\"x_line x_pdt-info\">\r\n<td class=\"x_products\">\r\n<div class=\"x_image\"><img src=\"https://res.litfad.net/site/img/item/2024/01/25/11408158/70x70.jpg\">\r\n</div>\r\n<div class=\"x_info\">\r\n<p class=\"x_name\">Set of 2 Modern Square Stone Coffee Tables with Storage and Drawers - 70 x 70 x 45 cm + 60 x 60 x 40 cm Gold White</p>\r\n<p class=\"x_attr\">70 x 70 x 45 cm + 60 x 60 x 40 cm, Gold, White </p>\r\n<p class=\"x_attr\">QTY:1&nbsp;&nbsp;SKU:2203196339</p>\r\n</div>\r\n</td>\r\n<td class=\"x_amount\">£175.33 </td>\r\n</tr>\r\n</tbody>\r\n</table>\r\n<div class=\"x_fee\">\r\n<h3>Order Grand Total:</h3>\r\n<p class=\"\"><span class=\"x_title\">Price:</span> <span class=\"x_value\">£175.33</span>\r\n</p>\r\n<p class=\"\"><span class=\"x_title\">Shipping Price:</span> <span class=\"x_value\">£14.58</span>\r\n</p>\r\n<p class=\"x_total\"><span class=\"x_title\">Total:</span> <span class=\"x_value\">£189.91</span>\r\n</p>\r\n</div>\r\n<p>If you have any question, please feel free to contact us, we’re glad to hearing from you.</p>\r\n<p class=\"x_sender\">Sincerely,<br>\r\nCustomer Care<br>\r\nwww.litfad.com<br>\r\n</p>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</body>\r\n</html>"
        }
    
    email = EmailCRUD.create_email(db, email_data)
    print(f"创建邮件成功: {email.subject}")
    return email

def test_get_service():
    db = next(get_db())
    service = EmailServiceCRUD.get_service(db, "6657")
    print(f"查询服务单成功: {service.title}")
    return service

def test_get_email():
    db = next(get_db())
    email = EmailCRUD.get_email(db, "7756")
    print(f"查询邮件成功: {email.subject}")
    return email

def test_update_service():
    db = next(get_db())
    service = EmailServiceCRUD.get_service(db, "6657")
    if service:
        print(f"更新前服务单状态: {service.status}")
        update_data = {
            "status": "99",
            "title": "服务单：6657（已更新）"
        }
        updated_service = EmailServiceCRUD.update_service(db, "6657", update_data)
        print(f"更新后服务单状态: {updated_service.status}")
        return updated_service

def test_query_relations():
    db = next(get_db())
    service = EmailServiceCRUD.get_service(db, "6657")
    if service:
        print(f"服务单: {service.title}")
        for email in service.emails:
            print(f"关联邮件: {email.email_id}")
            print(f"关联邮件主题: {email.subject}")
            print()

def test_delete_service():
    db = next(get_db())
    result = EmailServiceCRUD.delete_service(db, "6657")
    if result:
        print("删除服务单成功")
    else:
        print("删除服务单失败")

def main():
    
    try:
        # 1. 测试创建表
        test_create_tables()

        # 2. 测试添加服务单、邮件
        service = test_create_service()
        email = test_create_email()

        # 3. 测试查询服务单、邮件


        print("\n 测试完成！")
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    main()