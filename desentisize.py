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


a = "1228291335@qq.com"
b = "17621063414"
c = "021-65979152"

print(match_email(a))
print(match_telphone(b))
print(match_mobel(c))
