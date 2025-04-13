import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def crawl_keywords(keywords, company_name, environment="mobile", logger=print):
    results = []
    headers_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 Safari/605.1.15',
    ]

    for keyword in keywords:
        logger(f"▶ 키워드: {keyword}")

        if environment == "mobile":
            main_url = f"https://m.search.naver.com/search.naver?query={keyword}"
            full_url = f"https://m.ad.search.naver.com/search.naver?where=m_expd&query={keyword}"
            referer = "https://m.naver.com/"
            main_selector = ("div", "txt_area")
            full_selector = ("div", "tit_wrap")
        else:
            main_url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_sly.hst&fbm=0&acr=1&ie=utf8&query={keyword}"
            full_url = f"https://ad.search.naver.com/search.naver?where=ad&query={keyword}"
            referer = "https://naver.com/"
            main_selector = ("a", "lnk_head")
            full_selector = ("span", "lnk_tit")

        headers = {
            'User-Agent': random.choice(headers_list),
            'Referer': referer,
            'Accept-Language': 'ko-KR,ko;q=0.8'
        }

        try:
            soup = BeautifulSoup(requests.get(main_url, headers=headers).content, 'html.parser')
            ad_items = soup.find_all(main_selector[0], class_=main_selector[1])
        except Exception as e:
            logger(f"  [에러] 메인 요청 실패: {e}")
            results.append([keyword, '', 'Error'])
            continue

        found = False
        for idx, item in enumerate(ad_items, start=1):
            if company_name in item.get_text():
                logger(f"  ✔ 메인 노출 확인 (순위 {idx})")
                results.append([keyword, 'True', idx])
                found = True
                break

        if not found:
            logger("  ✖ 메인에서 발견 안 됨, 전체 목록 검색 시도...")
            try:
                soup_all = BeautifulSoup(requests.get(full_url, headers=headers).content, 'html.parser')
                all_ads = soup_all.find_all(full_selector[0], class_=full_selector[1])
                for idx, item in enumerate(all_ads[:10], start=1):
                    if company_name in item.get_text():
                        logger(f"  ✔ 전체 목록 발견 (순위 {idx})")
                        results.append([keyword, 'False', idx])
                        break
                else:
                    logger("  ✖ 전체 목록에도 없음")
                    results.append([keyword, 'False', '<10'])
            except Exception as e:
                logger(f"  [에러] 전체 목록 요청 실패: {e}")
                results.append([keyword, 'False', 'Error'])

### 10위까지 제한
        # if not found:
        #     logger("  ✖ 메인에서 발견 안 됨, 전체 목록 검색 시도...")
        #     try:
        #         soup_all = BeautifulSoup(requests.get(full_url, headers=headers).content, 'html.parser')
        #         all_ads = soup_all.find_all(full_selector[0], class_=full_selector[1])
        #         for idx, item in enumerate(all_ads[:10], start=1):
        #             if company_name in item.get_text():
        #                 logger(f"  ✔ 전체 목록 발견 (순위 {idx})")
        #                 results.append([keyword, 'False', idx])
        #                 break
        #         else:
        #             logger("  ✖ 전체 목록에도 없음")
        #             results.append([keyword, 'False', '<10'])
        #     except Exception as e:
        #         logger(f"  [에러] 전체 목록 요청 실패: {e}")
        #         results.append([keyword, 'False', 'Error'])

        time.sleep(random.uniform(2, 4))

    return pd.DataFrame(results, columns=["키워드", "상위노출여부", "순위"])
