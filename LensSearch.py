import requests
import json
import csv
import http.cookiejar as cookielib
from requests import utils


class LensSearch:

    # 构造函数
    def __init__(self, lensid, start, size):
        self.lensid = lensid
        self.start = start
        self.size = size
        self.base_url = "https://www.lens.org/lens/api/search/patent"

    # 根据id搜索专利
    def search_by_lensid(self):
        url = self.base_url + "?npl.must=" + self.lensid
        headers = \
            {
                "authority": "www.lens.org",
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "content-type": "application/json",
                "dnt": "1",
                "origin": "https://www.lens.org",
                "sec-ch-ua": "\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }
        playload = \
            {
                "size": self.size,
                "sort": [
                    {
                        "earliest_priority_claim_date": "desc"
                    }
                ],
                "_source": {
                    "includes": [
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
                },
                "from": self.start
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
f = open('resultFile17.csv', 'w', encoding='utf-8', newline="")
#  2.基于文件对象构建csv写入对象
csv_write = csv.writer(f)
#  3.构建列表头
csv_write.writerow(['lens_id', 'displayKey', 'record_lens_id', 'date_published', 'publication_type',
                    'earliest_priority_claim_date',  'title_en_text', 'applicant_name', 'applicant_residence',
                    'inventor_name', 'inventor_residence', 'class_ipcr_symbol', 'reference_cited_patent_lens_id',
                    'reference_cited_patent_count', 'reference_cited_npl_count', 'reference_cited_npl_resolved_count',
                    'cited_by_patent_count', 'legal_status_patent_status'])

# 读取csv文件,获取lensid
csv_reader = csv.reader(open('origin_id.csv', 'r', encoding='utf-8'))
for row in csv_reader:
    start = 0
    size = 50
    # 首次请求一条数据,获取总条数
    lens_search = LensSearch(row[0], start, 1)
    result = lens_search.search_by_lensid()
    print(result)
    # json字符串格式转字典
    result_dict = json.loads(result)
    # 总条数
    totalHits = result_dict['totalHits']
    if totalHits == 0:
        break
    while start < totalHits:
        lens_search = LensSearch(row[0], start, size)
        # 下一次请求的起始位置
        start = start + size
        result = lens_search.search_by_lensid()
        result_dict = json.loads(result)
        # 遍历每一条数据
        hits = result_dict['hits']

        for hit in hits:
            row_list = [row[0]]
            print('----------start=' + str(start) + ', size=' + str(size))
            displayKey = hit['displayKey']
            # print(displayKey)
            row_list.append(displayKey)
            document = hit['document']
            record_lens_id = document['record_lens_id']
            # print(record_lens_id)
            row_list.append(record_lens_id)
            date_published = document['date_published']
            # print(date_published)
            row_list.append(date_published)
            publication_type = document['publication_type']
            # print(publication_type)
            row_list.append(publication_type)
            earliest_priority_claim_date = document['earliest_priority_claim_date']
            # print(earliest_priority_claim_date)
            row_list.append(earliest_priority_claim_date)
            title_en = document['title'].get('en', [])
            title_en_text = []
            if title_en:
                for text_en in title_en:
                    title_en_text.append(text_en.get('text', '--'))
            else:
                title_en_text.append(['--'])
            # print(title_en_text)
            row_list.append(title_en_text)
            applicant = document['applicant']
            applicant_name = []
            applicant_residence = []
            for applicant_en in applicant:
                applicant_name.append(applicant_en['name'])
                applicant_residence.append(applicant_en.get('residence', '-'))
            # print(applicant_name)
            row_list.append(applicant_name)
            # print(applicant_residence)
            row_list.append(applicant_residence)
            inventor = document['inventor']
            inventor_name = []
            inventor_esidence = []
            for inventor_en in inventor:
                inventor_name.append(inventor_en['name'])
                inventor_esidence.append(inventor_en.get('residence', '-'))
            # print(inventor_name)
            row_list.append(inventor_name)
            # print(inventor_esidence)
            row_list.append(inventor_esidence)

            class_ipcr = document['class_ipcr']
            class_ipcr_symbol = []
            for ipcr in class_ipcr:
                class_ipcr_symbol.append(ipcr['symbol'])
            # print(class_ipcr_symbol)
            row_list.append(class_ipcr_symbol)

            reference_cited = document['reference_cited']
            reference_cited_patent_lens_id = ''
            for reference_cited_en in reference_cited:
                reference_cited_patent_lens_id += reference_cited_en['patent']['lens_id']
                reference_cited_patent_lens_id += ','
            # print(reference_cited_patent_lens_id)
            row_list.append(reference_cited_patent_lens_id)

            reference_cited_patent_count = document['reference_cited.patent_count']
            # print(reference_cited_patent_count)
            row_list.append(reference_cited_patent_count)
            reference_cited_npl_count = document['reference_cited.npl_count']
            # print(reference_cited_npl_count)
            row_list.append(reference_cited_npl_count)
            reference_cited_npl_resolved_count = document['reference_cited.npl_resolved_count']
            # print(reference_cited_npl_resolved_count)
            row_list.append(reference_cited_npl_resolved_count)
            cited_by_patent_count = document['cited_by']['patent_count']
            # print(cited_by_patent_count)
            row_list.append(cited_by_patent_count)
            legal_status_patent_status = document['legal_status']['patent_status']
            # print(legal_status_patent_status)
            row_list.append(legal_status_patent_status)

            #  4.写入csv文件
            csv_write.writerow(row_list)

#  5.关闭文件
f.close()
