import requests
import tools.des as des
import re
import json
import datetime
import time
import tools.thread as thread
import random


class BadmintonBooking(object):

    def __init__(self, username, password, phone, booking_time, booking_field_number):

        self.username = username
        self.password = password
        self.phone = phone
        self.booking_time = booking_time
        self.booking_field_number = booking_field_number
        # self.booking_time = "17:30-19:30"
        # self.booking_field_number = 6

        # print(self.username, self.booking_time, self.booking_field_number)

        self.client = requests.session()

        self.csrf_token = ""
        self.workflow_id = ""
        self.login_status = False

        self.school_area = ["大学城校区", "桂花岗校区"]
        self.booking_item = ["羽毛球"]
        self.booking_location = ["体育馆羽毛球场", "风雨跑廊羽毛球场"]

    def __login(self):
        new_cas_url = 'https://newcas.gzhu.edu.cn/cas/login'

        res = self.client.get(new_cas_url)
        lt = re.findall(r'name="lt" value="(.*)"', res.text)

        login_form = {
            'rsa': des.get_rsa(self.username, self.password, lt[0]),
            'ul': len(self.username),
            'pl': len(self.password),
            'lt': lt[0],
            'execution': 'e1s1',
            '_eventId': 'submit',
        }

        resp = self.client.post(new_cas_url, data=login_form)
        print("visited", resp.url)
        self.login_status = True

        # return True

    # core function
    def exec(self):
        # 一次预定7个场次
        for num in range(7):
            booking_field_number = num+1

            t = thread.Thread(
                name="field-{}-task".format(booking_field_number),
                target=self.single_exec,
                args=(booking_field_number,)  # 加入逗号，保证元组可迭代
            )
            thread.append_to_thread_list(t)

    def single_exec(self, booking_field_number):

        # 随机等待
        time.sleep(1*random.uniform(0, 20))

        self.__login()

        self.__login_check()

        self.__navigate_to_website_and_get_csrf_token()

        mission_url = self.__get_mission_url()

        step_id = self.__get_step_id(mission_url)

        data_template = self.__get_booking_data_template(step_id)

        request_data = self.__construct_booking_request_data(
            data_template, step_id, booking_field_number)

        self.__send_booking_request_and_confirm_application(request_data)

    # private functions

    def __login_check(self):
        if self.login_status == False:
            raise Exception("please call login() before calling this method!")

    def __navigate_to_website_and_get_csrf_token(self):
        res = self.client.get(
            'https://usc.gzhu.edu.cn/infoplus/form/TYCDYY/start')
        self.csrf_token = re.findall(
            r'<meta itemscope="csrfToken" content="(?P<token>.*?)">', res.text)[0]
        self.workflow_id = re.findall(
            r'workflowId = "(?P<tt>.*?)";', res.text)[0]

    def __get_mission_url(self):

        form_preview = {
            'workflowId': self.workflow_id,
            'rand': '114.514',
            'width': '932',
            'csrfToken': self.csrf_token
        }

        res_review = self.client.post(
            'https://usc.gzhu.edu.cn/infoplus/interface/preview', data=form_preview)
        preview_data = json.loads(res_review.text)['entities'][0]['data']

        form_get_url = {
            'idc': 'TYCDYY',
            'release': '',
            'csrfToken': self.csrf_token,
            # dump后保持中文
            'formData': json.dumps(preview_data, ensure_ascii=False),
            'lang': 'zh'
        }
        res_get_url = self.client.post(
            'https://usc.gzhu.edu.cn/infoplus/interface/start', data=form_get_url)
        # get URL with stepId from response
        url = json.loads(res_get_url.text)['entities'][0]
        return url

    def __get_step_id(self, url):
        stepId = re.findall(r'form/(?P<id>.*?)/render', url)[0]
        return stepId

    def __get_booking_data_template(self, step_id):
        form = {
            'stepId': step_id,
            'instanceId': '',
            'admin': 'False',
            'rand': '114.514',
            'width': '1536',
            'lang': 'zh',
            'csrfToken': self.csrf_token
        }

        self.client.headers.update(
            {'referer': 'https://usc.gzhu.edu.cn/infoplus/form/TYCDYY/start'})
        data = self.client.post(
            url='https://usc.gzhu.edu.cn/infoplus/interface/render', data=form)

        entity = json.loads(data.text)['entities']
        if len(entity) == 0:
            raise Exception(data.text)
        data_json = entity[0]

        return data_json

    # 指定时间和场次
    def __specify_time_and_field(self, time, field_number):
        # 6个时间段，7个场地
        booking_time_choices = {
            "8:30-10:30": 1,
            "08:30-10:30": 1,  # 冗余
            "10:30-12:30": 2,
            "13:30-15:30": 3,
            "15:30-17:30": 4,
            "17:30-19:30": 5,
            "19:30-21:30": 6,
        }

        # eg. choice_list = [True, False,False,...,False]
        choice_list = []
        for i in range(6*7):
            choice_list.append(False)

        # 注意数组下标，从0开始，所以最后的下标要-1
        choice_list[(booking_time_choices[time]-1)
                    * 7 + field_number - 1] = True

        return choice_list

    def __construct_booking_request_data(self, data_json, step_id, booking_field_number):
        # get data
        form_data = data_json['data']

        # print("表单数据模板", form_data)

        # get boundFields
        field = ''
        for key in data_json['fields']:
            field += key
            field += ','
        field = field[:-1]

        # update form_data
        # form_data['fieldSJD_Name'] = self.booking_time
        form_data['fieldLXFS'] = self.phone
        form_data['fieldXQ'] = self.school_area[0]
        form_data['fieldYYXM'] = self.booking_item[0]
        form_data['fieldXZDD'] = self.booking_location[1]
        form_data['fieldYYRQ'] = "周日"
        form_data['fieldZJ'] = "周日"
        # 预约次日的场次
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        form_data['fieldYYRQ_Name'] = tomorrow.strftime("%Y-%m-%d")

        print("预约时间", form_data['fieldYYRQ_Name'])

        form_data['groupCDXXList'] = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, - \
            1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, - \
            1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1

        form_data['fieldSJD'] = "8:30-10:30", "8:30-10:30", "8:30-10:30", "8:30-10:30", "8:30-10:30", "8:30-10:30", "8:30-10:30", "10:30-12:30", "10:30-12:30", "10:30-12:30", "10:30-12:30", "10:30-12:30", "10:30-12:30", "10:30-12:30", "13:30-15:30", "13:30-15:30", "13:30-15:30", "13:30-15:30", "13:30-15:30", "13:30-15:30", "13:30-15:30", "15:30-17:30", "15:30-17:30", "15:30-17:30", "15:30-17:30", "15:30-17:30", "15:30-17:30", "15:30-17:30", "17:30-19:30", "17:30-19:30", "17:30-19:30", "17:30-19:30", "17:30-19:30", "17:30-19:30", "17:30-19:30", "19:30-21:30", "19:30-21:30", "19:30-21:30", "19:30-21:30", "19:30-21:30", "19:30-21:30", "19:30-21:30"
        form_data["fieldTYXM"] = "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球", "羽毛球"
        form_data["fieldYYDD"] = "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场", "风雨跑廊羽毛球场"
        form_data["fieldYYCD"] = "1号场", "2号场", "3号场", "4号场", "5号场", "6号场", "7号场", "1号场", "2号场", "3号场", "4号场", "5号场", "6号场", "7号场", "1号场", "2号场", "3号场", "4号场", "5号场", "6号场", "7号场", "1号场", "2号场", "3号场", "4号场", "5号场", "6号场", "7号场", "1号场", "2号场", "3号场", "4号场", "5号场", "6号场", "7号场", "1号场", "2号场", "3号场", "4号场", "5号场", "6号场", "7号场"
        form_data["fieldYYZT"] = "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约",
        "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约", "未预约"
        form_data["fieldYLLY"] = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        # form_data['fieldXZ'] = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
        #                         False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        form_data['fieldXZ'] = self.__specify_time_and_field(
            self.booking_time, booking_field_number)
        print(form_data['fieldXZ'])

        form_data['fieldFZPD'] = "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生",
        "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生", "师生"
        form_data['fieldSFBZ'] = ""
        form_data['fieldYYSFjtsj'] = ""
        form_data['fieldQXYYjtsj'] = ""
        form_data['fieldYZYMFQ'] = 9999207.382511012

        # print("拼装后的数据", form_data)

        request_data = {
            'stepId': step_id,
            'actionId': 1,
            'formData': json.dumps(form_data),
            'timestamp': str(int(time.time())),
            'rand': '114.514191981',
            'boundFields': field,
            'csrfToken': self.csrf_token,
            'lang': 'zh'
        }

        # # 测试字段拼装情况
    #     print()
    #     print("绑定字段", request_data['boundFields'])

        # print()
        # for v in ["fieldXH", "fieldZJ", "fieldSFMZMB", "fieldXM", "fieldLSH",
        #           "fieldSQSJ", "fieldYYSFjtsj", "fieldSFBZ", "fieldYYCD", "fieldXY",
        #           "fieldYZYMFQ", "fieldXZDD", "fieldXZ", "fieldXQ", "fieldTYXM", "fieldFZPD",
        #           "fieldYYXM", "fieldSF", "fieldYLLY", "fieldYYDD", "fieldYYRQ", "fieldSJD",
        #           "fieldLXFS", "fieldQXYYjtsj", "fieldYYZT"]:
        #     # print(v)
        #     print(v, form_data[v])

        # print()
        # print(json.dumps(request_data))

        return request_data

    def __send_booking_request_and_confirm_application(self, request_data):

        # send request
        resp = self.client.post(
            url='https://usc.gzhu.edu.cn/infoplus/interface/listNextStepsUsers', data=request_data)

        print("")
        print(resp.text)

        if json.loads(resp.text)['errno'] != 0:
            raise Exception("booking error: {}".format(resp.text))

        # confirm application
        request_data.update(
            {
                'remark': '否',
                'rand': '268.121261',
                'nextUsers': '{}',
            }
        )

        resp = self.client.post(
            url='https://usc.gzhu.edu.cn/infoplus/interface/doAction', data=request_data)

        if json.loads(resp.text)['errno'] != 0:
            raise Exception("booking confirm error: {}".format(resp.text))
