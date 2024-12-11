import requests
import json
import csv
import http.cookiejar as cookielib
from requests import utils
from sympy import true


class LensSearch:

    # 构造函数
    def __init__(self, lensid):
        self.lensid = lensid
        self.base_url = "https://www.lens.org/lens/api/search/patent"

    # 根据id搜索专利
    def search_by_lensid(self):
        url = self.base_url + "?q=lens_id%3A%22" + self.lensid + "%22&st=true&e=false&f=false&l=en"
        headers = \
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                "content-type": "application/json",
                "origin": "https://www.lens.org",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                "x-lens-record-history": "true"
            }
        playload = \
            {
                "size": 10,
                "from": 0,
                "_source": [
                    "abstract",
                    "agent",
                    "applicant",
                    "application_reference.date",
                    "application_reference.doc_number",
                    "application_reference.kind",
                    "application_reference.jurisdiction",
                    "assistant_examiner",
                    "cited_by.patent_count",
                    "cited_by.patent.lens_id",
                    "cites_patent",
                    "claim",
                    "class_cpc",
                    "class_ipcr",
                    "class_national",
                    "date_published",
                    "doc_key",
                    "doc_number",
                    "earliest_priority_claim_date",
                    "examiner",
                    "family.extended.id",
                    "family.extended.size",
                    "family.simple",
                    "family.simple.id",
                    "family.simple.size",
                    "has_abstract",
                    "has_claim",
                    "has_description",
                    "has_docdb",
                    "has_examiner",
                    "has_full_text",
                    "has_title",
                    "inventor",
                    "jurisdiction",
                    "kind",
                    "legal_status",
                    "lens_internal.legacy_pub_key",
                    "npl_citation_count",
                    "owner_all",
                    "patent_citation_count",
                    "primary_examiner",
                    "priority_claim",
                    "publication_type",
                    "record_lens_id",
                    "reference_cited.npl_count",
                    "reference_cited.npl_resolved_count",
                    "reference_cited.patent_count",
                    "reference_cited.patent.lens_id",
                    "sequence",
                    "title"
                ]
            }

        # 定义cookiejar格式
        cookiejar = cookielib.MozillaCookieJar()
        # 从文件中读取cookie文件到cookiejar
        cookiejar.load(filename='cookie.lens.txt', ignore_discard=True, ignore_expires=True)
        # 从cookiejar中获取cookie内容
        cookies = requests.utils.dict_from_cookiejar(cookiejar)
        # 创建请求的request
        response = requests.post(url, data=json.dumps(playload), headers=headers, cookies=cookies)

        if response.status_code == 200:
            return response.text
        else:
            print(self.lensid + '没有查询到相关专利')
            return None

#  1.创建文件对象
f = open('resultNew10.csv', 'a+', encoding='utf-8', newline="")
#  2.基于文件对象构建csv写入对象
csv_write = csv.writer(f)
#  3.构建列表头 发VF:i-
# csv_write.writerow(['origin_id', 'publication_type', 'applicant_residence', 'inventor_residence',
#                     'reference_cited_patent_count', 'cited_by_patent_count', 'reference_cited_patent_lensid'])

# 读取csv文件,获取lensid
csv_reader = csv.reader(open('origin_id.csv', 'r', encoding='utf-8'))
for row in csv_reader:
    print(row[0])
    lens_search = LensSearch(row[0])
    result = lens_search.search_by_lensid()
    # json字符串格式转字典
    result_dict = json.loads(result)
    row_list = [row[0]]

    document = result_dict['hits'][0]['document']
    publication_type = document['publication_type']
    row_list.append(publication_type)

    applicants = document['applicant']
    applicant_residence = []
    for applicant in applicants:
        applicant_residence.append(applicant.get('residence', '-'))
    row_list.append(applicant_residence)

    inventors = document['inventor']
    inventor_residence = []
    for inventor in inventors:
        inventor_residence.append(inventor.get('residence', '-'))
    row_list.append(inventor_residence)

    reference_cited_patent_count = document['reference_cited.patent_count']
    row_list.append(reference_cited_patent_count)

    cited_by_patent_count = document['cited_by']['patent_count']
    row_list.append(cited_by_patent_count)

    reference_cited_patent_lensid = []
    reference_cited_list = document['reference_cited']
    for reference_cited in reference_cited_list:
        reference_cited_patent_lensid.append(reference_cited['patent'].get('lens_id', '-'))
    row_list.append(reference_cited_patent_lensid)

    # 写入csv文件
    csv_write.writerow(row_list)

#  5.关闭文件
f.close()
