from bs4 import BeautifulSoup
import re

def get_email_content(html_content):
    """提取邮件内容"""
    patten = r'(\\\\r|\\\\n|\\\\t|\\r|\\n|\\t|[\r\n\t])'
    content = re.sub(patten, '', html_content)

    soup = BeautifulSoup(content, 'lxml')
    content = soup.get_text(separator="\n")
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    cleaned_text = "\n".join(lines)
    return cleaned_text


def parse_html_email(html_content):
    """只提取正文内容，去掉引用和签名"""
    # 步骤1：提取<body>标签内的内容
    body_pattern = re.compile(r'(<body[^>]*>(.*?)</body>)', re.DOTALL)
    body_match = body_pattern.search(html_content)
    if not body_match:
        return "No body tag found"
    
    content = body_match.group(1)
    # 步骤2：删除所有带引号的\r\n（包括引号）
    patten = r'(\\\\r|\\\\n|\\\\t|\\r|\\n|\\t|[\r\n\t])'
    content = re.sub(patten, '', content)
    

    # 步骤3: 删除所有的引用内容
    quote_patterns = [
        # 163邮箱的引用模式
        r'<div id=\\*"appendonsend"\\*>.*?</body>',  
        r'<div id=["\']appendonsend["\']>.*?</body>',
        r'<div[^>]+id=(?:\\*["\'])?appendonsend(?:\\*["\'])?[^>]*>.*?</body>',
        
        # Outlook的引用模式
        r'<div style="border:none;border-top:solid #[A-Z0-9]{6}.*?<div class="OutlookMessageHeader">.*?</div>',
        r'<div style="border:none;border-top:solid.*?class=3D"OutlookMessageHeader".*?</div>',
        
        # Gmail的引用模式
        r'<div class="gmail_quote">.*?</div>',
        r'<blockquote class="gmail_quote".*?>.*?</blockquote>',
        
        # Yahoo邮箱的引用模式
        r'<div id="yahoo_quoted_\d+".*?>.*?</div>',
        r'<blockquote class="yahoo_quoted".*?>.*?</blockquote>',
        
        # 通用引用模式
        r'<blockquote.*?>.*?</blockquote>',  # 通用引用块
        r'<div class="[^"]*quoted[^"]*".*?>.*?</div>',  # 包含quoted的div
        r'<div class="[^"]*forward[^"]*".*?>.*?</div>',  # 转发内容
        r'<div style="[^"]*border-left[^"]*">.*?</div>'  # 带左边框的引用样式
    ]
    for pattern in quote_patterns:
        original_length = len(content)
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        # if len(content) != original_length:
        #     print(f"匹配到引用内容，使用模式: {pattern[:50]}...")
        

    # 步骤4: 去掉签名
    # soup = BeautifulSoup(content, 'html.parser')
    soup = BeautifulSoup(content, 'lxml')

    patten = [  # 常见的邮箱签名标签
        "mail-signiture",
        "signature",
    ]
    for tag in patten:
        for match in soup.find_all("div", class_=re.compile
        (tag, re.IGNORECASE)):
            match.decompose()
    
    # 步骤5: 获取纯文本内容
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cleaned_text = "\n".join(lines)
    return cleaned_text
    


if __name__ == '__main__':
    with open ('email_example.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    email_body = parse_html_email(html_content)
    print(email_body)
