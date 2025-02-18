# -*- coding: utf-8 -*-
"""
    * 功能：
        1.福利彩票 - 双色球  历史数据获取
        2.福利彩票 - 双色球  历史数据条件预测分析
        3.福利彩票 - 双色球  每期数据条件预测分析
        4.福利彩票 - 双色球  每期预测数据对比实际数据的验证(单次验证/条件循环验证),获取规则
    :Copyright © Leon. 23:25 06-07-2023.
"""
import requests
import datetime
import os
import re

# 数据网站
data_url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/" \
"kjxx/findDrawNotice?name=ssq&systemType=PC&pageNo=__PAGENO__&pageSize=__PAGESIZE__"

# 文件名称
unionLotto_grap_name = 'log/unionLotto_grap'
unionLotto_hist_name = 'log/unionLotto_hist'
analysis_fore_name = 'log/analysis_fore'
analysis_hist_name = 'log/analysis_hist'

# NO1: 每期数据 - 分析时间段
interval_days = 30
# NO2: 每期数据 - 反复次数 - 分析时间段
appear_days = 15

# 抓取
class grap():

    def __init__(self,
                 begin_page: int = 1,
                 end_page: int = None,
                 page_count: int = 100,
                 data_url: str = data_url):
        self.begin_page = begin_page
        self.end_page = end_page
        self.page_count = page_count
        self.data_url = data_url
        try:
            print('========= grap begin =========')
            # 获取网站导航栏数据
            replacements = {"__PAGESIZE__": str(self.page_count)}
            for filter_old_val, filter_new_val in replacements.items():
                self.data_url = self.data_url.replace(filter_old_val, filter_new_val)
            temp_url = self.data_url.replace('__PAGENO__', str(self.begin_page))
            response = self.request_data(page_url=temp_url)
            if response.status_code == 200:
                data = response.json()
                if data['state'] != 0:
                    print(self.get_cur_time() + " 首次加载程序出错1: (begin_page:{})".
                          format(str(self.begin_page)))
                else:
                    for step, dataval in enumerate(data['result']):
                        self.log_str = dataval['code']+'-'+dataval['red']+'-'+dataval['blue']
                        self.write_log()

                    if self.end_page is not None:
                        page_end = self.end_page
                    else:
                        page_end = int(data['pageNum'])+1

                    for cur_page in range(self.begin_page+1, page_end):
                        try:
                            temp_url = self.data_url.replace('__PAGENO__', str(cur_page))
                            response = self.request_data(page_url=temp_url)
                            if response.status_code == 200:
                                data = response.json()
                                if data['state'] != 0:
                                    print(self.get_cur_time() + " 首次加载程序出错2:(begin_page:{})".
                                          format(str(cur_page)))
                                else:
                                    for step, dataval in enumerate(data['result']):
                                        self.log_str = dataval['code']+'-'+dataval['red']+'-'+dataval['blue']
                                        self.write_log()
                            else:
                                print(self.get_cur_time() + " 请求出错2，状态码：{}(begin_page:{})".
                                      format(str(response.status_code), str(cur_page)))
                        except Exception as e:
                            print(self.get_cur_time() + " 程序异常2 - {}(begin_page:{})".
                                  format(str(e), str(self.cur_page)))
            else:
                print(self.get_cur_time() + " 请求出错1，状态码：{}(begin_page:{})".
                      format(str(response.status_code), str(self.begin_page)))
        except Exception as e:
            print(self.get_cur_time() + " 程序异常1 - {}(begin_page:{})".
                  format(str(e), str(self.begin_page)))
        print('========= grap end =========')

    # 写入文件日志并输出
    def write_log(cls):
        # 写入文件日志并输出
        with open(unionLotto_grap_name+'.txt', 'a', encoding='utf-8') as f:
            f.write(cls.log_str + '\n')
        print(cls.log_str)

    # 获取当前时间
    def get_cur_time(cls):
        current_time = datetime.datetime.now()
        return str(current_time.strftime('%Y-%m-%d %H:%M:%S'))

    # 请求网站数据
    def request_data(cls, page_url: str = None, params: dict = {}):
        if page_url is None:
            response = requests.get('http://www.this-is-unionLotto-test.com')
            response.status_code = 100003
        else:
            if bool(params):
                response = requests.post(page_url, params=params)
            else:
                response = requests.get(page_url)
        return response

# 分析
class analysis():
    def __init__(self,
                 interval_days: int = interval_days,
                 appear_days: int = appear_days):
        self.interval_days = interval_days
        self.appear_days = appear_days
        print('========= analysis begin =========')
        if os.path.exists(unionLotto_hist_name + '.txt') and \
                os.path.getsize(unionLotto_hist_name + '.txt') > 0:
            with open(unionLotto_hist_name + '.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]

            # 数据详情
            data_interval = []
            # 数据日期
            self.date_interval = []
            data_interval_count = len(lines)
            for num, elem in enumerate(lines):
                cur_number = elem.split('-')
                date = cur_number[0]
                reds = cur_number[1].split(',')
                blue = cur_number[-1]
                data_interval.append([reds, blue])
                self.date_interval.append(date)
            del lines

            # 分析预测文件内数据
            analysis_cur_exist = False
            cur_analysis_done_name = analysis_fore_name + "(" + str(int(self.date_interval[0]) + 1) + '期).txt'
            if os.path.exists(cur_analysis_done_name) and os.path.getsize(cur_analysis_done_name) > 0:
                cur_clear_state = False
                with open(cur_analysis_done_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                nums_str = re.search('_(.*)_', lines[0])
                end_str = re.search('analysis end', lines[-1])
                if nums_str is not None and end_str is not None:
                    nums_str = nums_str.group(0)
                    nums_arr = nums_str.replace('_', '').split('-')
                    cur_appear_days = int(nums_arr[0])
                    cur_interval_days = int(nums_arr[1])
                    if cur_appear_days == self.appear_days and cur_interval_days == self.interval_days:
                        # 数据已分析
                        analysis_cur_exist = True
                    else:
                        # 条件已更新 - 清空陈旧数据
                        cur_clear_state = True
                else:
                    # 有可能存在脏数据 - 清空
                    cur_clear_state = True

                if cur_clear_state:
                    with open(cur_analysis_done_name, "w"):
                        pass

            # 分析历史文件内数据
            analysis_hist_exist = False
            cur_last_date = 0
            cur_analysis_hist_name = analysis_hist_name + '.txt'
            if os.path.exists(cur_analysis_hist_name) and os.path.getsize(cur_analysis_hist_name) > 0:
                hist_clear_state = False
                with open(cur_analysis_hist_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                end_str = re.search('analysis end', lines[-1])
                # 最近日期
                if lines[0] is not None and lines[1] is not None and end_str is not None:
                    cur_last_date = int(lines[1].strip()[0:7])
                    cur_interval_days = re.search('_(.*)_', lines[0])
                    if cur_interval_days is not None:
                        cur_interval_days = int(cur_interval_days.group(0).replace('_', ''))
                        if cur_interval_days == self.interval_days:
                            # 数据已分析
                            analysis_hist_exist = True
                        else:
                            # 条件已更新 - 清空陈旧数据
                            hist_clear_state = True
                    else:
                        # 有可能存在脏数据 - 清空
                        hist_clear_state = True
                else:
                    # 有可能存在脏数据 - 清空
                    hist_clear_state = True

                if hist_clear_state:
                    with open(cur_analysis_hist_name, "w"):
                        pass

            # 文件内容待更新
            if not analysis_cur_exist or not analysis_hist_exist \
                    or cur_last_date != int(self.date_interval[0]):
                from collections import Counter
                # # NO1: 每期数据 - 分析时间段 (第二种方法)
                # for begin, begin_item in enumerate(data_interval):
                #     incision = data_interval[begin:begin + self.interval_days]
                #     # red number
                #     red_numbers = [red_num
                #                for red_key, incision_signal in enumerate(incision)
                #                for red_key2, red_num in enumerate(incision_signal[0])]
                #     red_number_dict = dict(Counter(red_numbers))
                #     data_interval[begin][0] = {red_num: red_number_dict.get(red_num, 0)
                #                                for red_key, red_num in enumerate(begin_item[0])}
                #     # blue number
                #     blue_numbers = [incision_signal[1]
                #                for blue_key, incision_signal in enumerate(incision)]
                #     blue_number_dict = dict(Counter(blue_numbers))
                #     data_interval[begin][1] = {begin_item[1]: blue_number_dict.get(begin_item[1], 0)}

                # NO1: 每期数据 - 分析时间段
                for begin, begin_item in enumerate(data_interval):
                    incision = data_interval[begin:begin + self.interval_days]
                    # 计数:在时间段内,每期number重复出现次数
                    index_red = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                    index_blue = 0
                    for signal_num, signal_val in enumerate(begin_item[0]):
                        for order, list_item in enumerate(incision):
                            if signal_val in list_item[0]:
                                index_red[signal_num] += 1
                    for order, list_item in enumerate(incision):
                        if begin_item[1] in list_item[1]:
                            index_blue += 1
                    # 赋值red各number
                    dict_red = {}
                    dict_blue = {}
                    for _index, elem in enumerate(data_interval[begin][0]):
                        dict_red[elem] = index_red[_index]
                        data_interval[begin][0] = dict_red
                    # 赋值blue number
                    dict_blue[data_interval[begin][1]] = index_blue
                    data_interval[begin][1] = dict_blue

                # NO2: 每期数据 - 反复次数分析
                most_appear_arr = [[], []]
                for first_index, first_elem in enumerate(data_interval):
                    if first_index <= self.appear_days - 1:
                        for second_index, red_number in enumerate(first_elem[0]):
                            red_times = first_elem[0][red_number]
                            most_appear_arr[0].append(red_times)
                        for second_index, blue_number in enumerate(first_elem[1]):
                            blue_times = first_elem[1][blue_number]
                            most_appear_arr[1].append(blue_times)

                # '历史反复最多次数' - 6个计数
                counter = Counter(most_appear_arr[0])
                most_appear_arr[0] = counter.most_common(6)
                counter = Counter(most_appear_arr[1])
                most_appear_arr[1] = counter.most_common(6)

                # 数据不全 - 填补(第一种) : 优先对比最小数字 再小一位,如最小数字小于2 对比最大数字 再大一位
                # _temp_list = []
                # if len(most_appear_arr[0]) != 6:
                #     for i in range(1, 6):
                #         if len(most_appear_arr[0]) != 6:
                #             for key, num in enumerate(most_appear_arr[0]):
                #                 _temp_list.append(num[0])
                #             _insert_num = min(_temp_list) - 1
                #             if min(_temp_list) <= 1:
                #                 _insert_num = max(_temp_list) + 1
                #             most_appear_arr[0].append((_insert_num, 0))
                #         else:
                #             break

                # 数据不全 - 填补(第二种) : 取中位数(长度为偶数,取中间最小位) 反复取值
                if len(most_appear_arr[0]) != 6:
                    for i in range(1, 6):
                        if len(most_appear_arr[0]) != 6:
                            sorted_most_arr = sorted([num[0]
                                                      for key, num in enumerate(most_appear_arr[0])])
                            mid_index = len(sorted_most_arr) // 2
                            if len(sorted_most_arr) % 2 == 0:
                                mid_index = mid_index - 1
                            most_appear_arr[0].append((sorted_most_arr[mid_index], 0))
                        else:
                            break

                # '预测当期反复次数' - 各少于'6个计数'1位
                second_appear_count = [[], []]
                for first_index, first_elem in enumerate(most_appear_arr[0]):
                    second_appear_count[0].append(first_elem[0] - 1)
                for first_index, first_elem in enumerate(most_appear_arr[1]):
                    second_appear_count[1].append(first_elem[0] - 1)
                del most_appear_arr

                # NO3: '预测当期number' - (次序忽略): 如不为0次的数字匹配不到则忽略
                num_all = [[], []]
                # red: 1--33
                for red_num in range(1, 34):
                    num_all[0].append(str(red_num).zfill(2))
                # blue: 1--16
                for blue_num in range(1, 17):
                    num_all[1].append(str(blue_num).zfill(2))

                # 预测当期number+反复次数
                appear_num = [[], []]
                appear_num_temp = [[], []]
                for first_index, first_elem in enumerate(data_interval):
                    # 分析 '时间段-1日' 前数据
                    if first_index <= self.interval_days - 2:
                        for second_index, red_number in enumerate(first_elem[0]):
                            red_times = first_elem[0][red_number]
                            if red_times in second_appear_count[0]:
                                if red_number not in appear_num_temp[0]:
                                    appear_num_temp[0].append(red_number)
                                    if (red_number, red_times) not in appear_num[0]:
                                        appear_num[0].append((red_number, red_times))
                        for second_index, blue_number in enumerate(first_elem[1]):
                            blue_times = first_elem[1][blue_number]
                            if blue_times in second_appear_count[1]:
                                if blue_number not in appear_num_temp[1]:
                                    appear_num_temp[1].append(blue_number)
                                    if (blue_number, blue_times) not in appear_num[1]:
                                        appear_num[1].append((blue_number, blue_times))

                # '预测当期反复次数'存在1位 且 一次未出现number
                if 0 in second_appear_count[0]:
                    for red_num in num_all[0]:
                        if red_num not in appear_num_temp[0]:
                            appear_num[0].append((red_num, 0))
                if 0 in second_appear_count[1]:
                    for blue_num in num_all[1]:
                        if blue_num not in appear_num_temp[1]:
                            appear_num[1].append((blue_num, 0))
                del appear_num_temp

                # '预测当期number分组'  - red number 按照反复次数次序进栈 blue number没有顺序
                choose_list = [[[], [], [], [], [], []], []]
                for red_index, red_nums in enumerate(appear_num[0]):
                    indexs = [num_key
                              for num_key, num_val in enumerate(second_appear_count[0])
                              if num_val == red_nums[1]]
                    for times_index, times_key in enumerate(indexs):
                        choose_list[0][times_key].append(red_nums[0])
                        choose_list[0][times_key] = list(set(choose_list[0][times_key]))
                    # index = second_appear_count[0].index(red_nums[1])
                    # choose_list[0][index].append(red_nums[0])
                    # choose_list[0][index] = list(set(choose_list[0][index]))
                for blue_index, blue_nums in enumerate(appear_num[1]):
                    choose_list[1].append(blue_nums[0])
                    choose_list[1] = list(set(choose_list[1]))

                # print(second_appear_count[0])
                # print(appear_num[0], len(appear_num[0]))
                # print(choose_list[0], len(choose_list[0]))
                # print(second_appear_count[1])
                # print(appear_num[1], len(appear_num[1]))
                # print(choose_list[1], len(choose_list[1]))
                # exit()

                # '预测当期组合'
                new_choose_list = []
                for red_0 in choose_list[0][0]:
                    for red_1 in choose_list[0][1]:
                        for red_2 in choose_list[0][2]:
                            for red_3 in choose_list[0][3]:
                                for red_4 in choose_list[0][4]:
                                    for red_5 in choose_list[0][5]:
                                        for blue_0 in choose_list[1]:
                                            new_choose_list.append([set([red_0,
                                                                         red_1,
                                                                         red_2,
                                                                         red_3,
                                                                         red_4,
                                                                         red_5]),
                                                                    set([blue_0])])
                choose_list = new_choose_list
                del new_choose_list

                # print(choose_list, len(choose_list))
                # exit()

                # 写入预测当期
                if not analysis_cur_exist:
                    choose_count = len(choose_list)
                    for first_index, elem_list in enumerate(choose_list):
                        if first_index == 0:
                            self.log_str = "********************以下为预测当期组合 _{}-{}_ (共{}条组合)********************".\
                                format(self.appear_days, self.interval_days, choose_count)
                            self.write_log()
                        self.log_str = str(elem_list)
                        self.write_log()
                        # print('预测当期', "\033[31m"+self.log_str+"\033[0m")
                    self.log_str = '*预测' + str(int(self.date_interval[0]) + 1) + '期 analysis end*'
                    self.write_log()
                    print('*预测' + str(int(self.date_interval[0]) + 1) + '期 analysis end*')
                else:
                    print("*预测{}期 analysis no update*".format(str(int(self.date_interval[0]) + 1)))

                # 写入预测历史
                if analysis_hist_exist and cur_last_date == int(self.date_interval[0]):
                    print("*hist analysis no update*")
                else:
                    if not analysis_hist_exist:
                        for first_index, elem_list in enumerate(data_interval):
                            if first_index == 0:
                                self.log_str = "***********************以下为分析数据 _{}_ (共{}条组合)***********************"\
                                    .format(self.interval_days, data_interval_count)
                                self.write_log(type='hist')
                            if first_index == data_interval_count - self.interval_days + 1:
                                self.log_str = '***********************以下数据剔除：参考数据不全***********************'
                                self.write_log(type='hist')
                            self.log_str = str(self.date_interval[first_index]) + ' ' + str(elem_list)
                            self.write_log(type='hist')
                        self.log_str = '*hist analysis end*'
                        self.write_log(type='hist')
                    else:
                        with open(cur_analysis_hist_name, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        # 插入最新数据
                        reverse_date_interval = self.date_interval[0:200][::-1]
                        # reverse_date_interval = self.date_interval[0:200].reverse()
                        reverse_data_interval = data_interval[0:200][::-1]
                        for _index, _date in enumerate(reverse_date_interval):
                            cur_date = int(lines[1].strip()[0:7])
                            if cur_date < int(_date):
                                print('add: ', str(_date) + ' ' + str(reverse_data_interval[_index]))
                                # 在最前列插入数据
                                lines.insert(1, str(_date) + ' ' + str(reverse_data_interval[_index]) + '\n')
                        del reverse_date_interval, reverse_data_interval
                        # 将修改后的内容写回文件
                        with open(cur_analysis_hist_name, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                    print('*hist analysis end*')
            elif analysis_cur_exist and analysis_hist_exist and cur_last_date == int(self.date_interval[0]):
                print("*预测{}期 analysis AND hist analysis no update*".
                      format(str(int(self.date_interval[0]) + 1)))
        else:
            print(unionLotto_hist_name + ' not exist')
        print("========= analysis end =========")

    # 写入文件日志并输出
    def write_log(cls, type =''):
        # 写入文件日志并输出
        cur_analysis_name = analysis_fore_name + "(" + str(int(cls.date_interval[0]) + 1) + '期).txt'
        if type == 'hist':
            cur_analysis_name = analysis_hist_name+'.txt'
        with open(cur_analysis_name, 'a', encoding='utf-8') as f:
            f.write(cls.log_str + '\n')
        # print(cls.log_str)

# 验证
class verification_once():

    def __init__(self,
                 datestr: str = None,
                 datalist: list = None):
        self.search_list = [datalist[0], datalist[1]]
        self.date = datestr

    def verify(cls):
        exist_num = 0
        verification_name = analysis_fore_name+'('+cls.date+'期).txt'
        print('========= verification_once begin =========')
        state_desc = 'error'
        verification_simple_name = ''
        for filter_old_val, filter_new_val in {".txt": '', 'log/': ''}.items():
            verification_simple_name = verification_name.replace(filter_old_val, filter_new_val)
        if os.path.exists(verification_name) and os.path.getsize(verification_name) > 0:
            with open(verification_name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for step, line in enumerate(lines):
                    if line.strip() and '*' not in line.strip():
                        red_str = str(eval(line.strip())[0])
                        blue_str = str(eval(line.strip())[1])
                        exist_num = 0
                        for red_key, red_num in enumerate(cls.search_list[0]):
                            if red_num in red_str:
                                exist_num += 1
                        for red_key, blue_num in enumerate(cls.search_list[1]):
                            if blue_num in blue_str:
                                exist_num += 1
                        if exist_num == 7:
                            print('验证结果: ',
                                  line.strip(),
                                  '第 '+str(step)+' 行 ['+verification_simple_name+']')
                            break
            if exist_num != 7:
                state_desc = 'no matching'
                print('验证结果: 未匹配到 [' + verification_simple_name + ']')
            else:
                state_desc = 'matching'
        else:
            print(verification_simple_name+' not exist')
        print('========= verification_once end =========')
        return state_desc


class verification_onceforall():
    def __init__(self,
                 range_begin: int = 10,
                 range_end: int = 1560,
                 step: int = 10,
                 interval: int = 15,
                 datestr: str = None,
                 datalist: list = None):
        self.range_begin = range_begin
        self.range_end = range_end
        self.step = step
        self.interval = interval
        self.datestr = datestr
        self.datalist = datalist

    def verify(cls):
        print('========= verification_onceforall begin =========')
        state_desc = 'no matching'
        for day in range(cls.range_begin, cls.range_end+1, cls.step):
            print("\ninterval_days:{} appear_days:{}".format(day, day + cls.interval))
            analysis(interval_days=day, appear_days=day + cls.interval)
            verification = verification_once(date=cls.datestr, data=cls.datalist)
            state_desc = verification.verify()
            if state_desc == 'error' or state_desc == 'matching':
                break
        print('========= verification_onceforall end =========')
        return state_desc

if __name__ == "__main__":
    # grap(begin_page=1, end_page=2, page_count=1)

    analysis(interval_days=30, appear_days=15)

    # verification = verification_once(datestr='2023065',
    #                                   datalist=[{'02', '14', '17', '20', '26', '33'}, {'14'}])
    # verification.verify()

    # verification = verification_onceforall(range_begin=30,
    #                                        range_end=1450,
    #                                        step=10,
    #                                        interval=15,
    #                                        datestr='2023065',
    #                                        datalist=[{'02', '14', '17', '20', '26', '33'}, {'14'}])
    # verification.verify()


    # print("{:.1f}".format(10 / 3), {'a': 10, 'b': 5, 'c': 20, 'd': 15}.items())
    # my_list = ['key1', 'key2', 'key3']
    # print({elem: 0 for elem in my_list}, {elem: index for index, elem in enumerate(my_list)})
