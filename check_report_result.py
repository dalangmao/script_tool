# -*- coding: utf-8 -*-
#__author__ = 'lishuai'

import sys
import time
import requests
from requests_ntlm import HttpNtlmAuth
from html.parser import HTMLParser

def get_response(url, user, passwd):
    #r = requests.get(url, auth=HttpNtlmAuth('domain\\svc_p_bi', 'Bre_0000'))
    session = requests.Session()
    session.auth = HttpNtlmAuth(user, passwd)
    r = session.get(url)
    try:
        if r.status_code == 200:
            print("The url:{0} connect success".format(url))
    except Exception as e:
        print("connect failure", e)
        sys.exit(1)
    return r

class Myparser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.handledtags = ['td']
        self.processing = None
        self.href_list = []
        self.table_list = []
        self.flag = False

    def handle_starttag(self, tag, attrs):
        def _attr(attrlist, attrname):
            for each in attrlist:
                if attrname == each[0]:
                    return each[1]
            return None
        if tag in self.handledtags:
            self.data = ''
            self.processing = tag
        if tag == 'a' and _attr(attrs, 'href'):
            href_dict = {}
            href_dict['href'] = _attr(attrs, 'href')
            self.href_list.append(href_dict)

        if tag == 'td' and _attr(attrs, 'class') == 'requestdetail-table-header':
            self.flag = True

    def handle_data(self, data):
        if self.flag == True:
            if self.processing:
                self.data += data

    def handle_endtag(self, tag):
        if tag == self.processing:
            if str(self.data):
                data_str = str(self.data)
                self.table_list.append(data_str)
                self.processing = None

def get_requestid_str(html_data):
    myparser = Myparser()
    myparser.feed(html_data.text)
    href_lists = myparser.href_list
    for i in href_lists:
        if "RequestDetails" in i['href']:
            requestid_str = i['href']
            return requestid_str

def get_detail_link(url, requestid_str):
    link_str_list = url.split("/")[2:-1]
    new_url = "http://" + '/'.join(link_str_list)
    detail_link = new_url + '/' + requestid_str
    return detail_link


def get_table_data(detail_html_data):
    myparser = Myparser()
    myparser.feed(detail_html_data.text)
    table_list = myparser.table_list
    data_dict = {}
    for i in range(len(table_list)):
        if i % 2 != 0:
            continue
        data_dict[str(table_list[i])] = table_list[i + 1]
        i = i + 2
        if i == 44:
            break
    return data_dict

def judge_report_result(data_dict):
    retry_flag = result_flag = False
    print("current Upload Request ID' is :", data_dict['Upload Request ID'])
    status_str = data_dict['Status']
    if 'Total Binaries Size (MB)' in data_dict.keys():
        binary_size = data_dict['Total Binaries Size (MB)']
        symbol_size = data_dict['Total Symbols Size (MB)']
    else:
        binary_size = symbol_size = ''
    if 'Total Source Size (MB)' in data_dict.keys():
        source_size = data_dict['Total Source Size (MB)']
    else:
        source_size = ''
    if status_str == 'OnUploadHold':
        print("current Upload Status is {0}, Upload Failure".format(status_str))
        print("Upload Failure")
        sys.exit(1)
    if status_str == 'Uploading':
        print("current Upload Status is {0} , Need Retry".format(status_str))
        retry_flag = True
    if status_str == 'Uploaded':
        print("status ok, need check size")
        # check binary size, minima is 3698.69
        # check symbole size, minima is 3559.42
        if binary_size != '' and symbol_size != '':
            if float(binary_size) < 3598.69 or float(symbol_size) < 3459.42:
                print("current Total Binaries size: {0}, Total Symbols Size: {1} ,all of abnormal".format(binary_size, symbol_size))
                sys.exit(1)
            else:
                print("Upload Success")
                result_flag = True
        # check source size, minima is 6061.06
        if source_size != '':
            if float(source_size) < 5961.06:
                print("current Total Source size: {0} is abnormal".format(source_size))
            else:
                print("Upload Success")
                result_flag = True
    return retry_flag, result_flag

def retry(check_url, requestid_str, user, passwd):
    detail_link = get_detail_link(check_url, requestid_str)
    detail_html_data = get_response(detail_link, user, passwd)
    data_dict = get_table_data(detail_html_data)
    retry_flag, result_flag = judge_report_result(data_dict)
    if retry_flag == True:
        time.sleep(300)
        retry(check_url, requestid_str, user, passwd)

def get_check_url(platform, build_number):
    print("current platform:", platform)
    windows_source_url = "http://cerservices.autodesk.com/SymbolCentral/Uploader/RequestSearchResult.aspx?productId=226&build="
    mac_source_url = "http://cerservices.autodesk.com/SymbolCentral/Uploader/RequestSearchResultMac.aspx?pl=NINVFUS&rl=R1&ma=%7b5A499737-CD26-423F-BFF8-40AE0C546F8C%7d&bu="
    if platform == 'windows':
        windows_build_number = transform_build_number(platform, build_number)
        windows_url = windows_source_url + windows_build_number
        return windows_url
    elif platform == 'mac':
        mac_build_number = transform_build_number(platform, build_number)
        mac_url = mac_source_url + mac_build_number
        return mac_url
    else:
        print("Please check platform")
        sys.exit(1)

def transform_build_number(platform, build_number):
    build_number_list = build_number.split('.')
    if platform == 'mac':
        build_str = '.'.join(build_number_list[:2])
        mac_build_number = build_number_list[2] + '.' + build_str
        print(mac_build_number)
        return mac_build_number
    elif platform == 'windows':
        windows_build_number = build_number
        return windows_build_number
    else:
        print("Please check platform")
        sys.exit(1)

def main():
    user = "svc_p_bi"
    passwd = "Bre_0000"
    #build_number = '2.1.6301'
    build_number = '2.0.4307'
    platform = 'windows'

    check_url = get_check_url(platform, build_number)
    html_data = get_response(check_url, user, passwd)
    requestid_str = get_requestid_str(html_data)
    retry(check_url, requestid_str, user, passwd)

if __name__ == '__main__':
    main()