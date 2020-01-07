import re

def match_telphone(data):
    p = re.compile(r"^1[3-9]\d{9}$")
    res = p.findall(data)
    return res

def match_email(data):
    p = re.compile(r"\w{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}")
    res = p.findall(data)
    return res

def match_idcard(data):
    p = re.compile(r"^[1-6]\d{5}[12]\d{3}(0[1-9]|1[12])(0[1-9]|1[0-9]|2[0-9]|3[01])\d{3}(\d|X|x)$")
    res = p.findall(data)
    return res

def match_mobel(data):
    p = re.compile(r"\d{3}-\d{8}|\d{4}-\d{7}")
    res = p.findall(data)
    return res

class Desensitization(object):
    def __init__(self, email=None, mobile=None, identity_card=None, address=None):
        self.email = email
        self.mobile = mobile
        self.identity_card = identity_card
        self.address = address

    def get_email_complex(self):
        # 通过@分开字符串
        mail_split_list = self.email.split('@')
        # 前面2位显示
        dis_mail_pre = mail_split_list[0][:2]
        # 其它位数隐藏
        hide_mail_pre = mail_split_list[0][2:]
        # 最后2位显示
        dis_mail_last = mail_split_list[-1][-2:]
        # 其它位数隐藏
        hide_mail_last = mail_split_list[-1][:-2]
        # 使用re.sub过滤
        result_hide_mail_pre = re.sub(hide_mail_pre, len(hide_mail_pre) * '*', hide_mail_pre)
        # 使用re.sub过滤
        result_hide_mail_last = re.sub(hide_mail_last, len(hide_mail_last) * '*', hide_mail_last)
        # 将结果集合起来
        desensitization_mail = dis_mail_pre + result_hide_mail_pre + '@' + result_hide_mail_last + dis_mail_last
        return desensitization_mail

    def get_email(self):
        hide_mail_content = self.email[2:-2]
        result = re.sub(hide_mail_content, len(hide_mail_content) * '*', self.email)
        return result

    def get_mobile(self):
        hide_mail_content = self.mobile[3:-4]
        result = re.sub(hide_mail_content, len(hide_mail_content) * '*', self.mobile)
        return result

    def get_identity_card(self):
        hide_identity_card = self.identity_card[3:-4]
        result = re.sub(hide_identity_card, len(hide_identity_card) * '*', self.identity_card)
        return result

    def get_address(self):
        hide_address_content = self.address[3:-3]
        result = re.sub(hide_address_content, len(hide_address_content) * '*', self.address)
        return result


if __name__ == "__main__":
    a = "1228291335@qq.com"
    b = "17621063414"
    c = "021-65979152"

    print(match_email(a))
    print(match_telphone(b))
    print(match_mobel(c))
    
    result_email = Desensitization(email='linqunbin@126.com')
    print(result_email.get_email())

    result_mobile = Desensitization(mobile='18911112222')
    print(result_mobile.get_mobile())

    result_id = Desensitization(identity_card='123123200001011234')
    print(result_id.get_identity_card())

    result_address = Desensitization(address="上海市虹口区某某路某某号123室")
    print(result_address.get_address())

