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

        # 환경별 URL 및 선택자 설정
        if environment == "mobile":
            main_url = f"https://m.search.naver.com/search.naver?query={keyword}"
            full_url = f"https://m.ad.search.naver.com/search.naver?where=m_expd&query={keyword}"
            referer = "https://m.naver.com/"
            # main_area_id = "power_link_body"
            full_area_id = "lst_type"
            name_tag = "span"
            class_name = "tit"
        else:
            main_url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_sly.hst&fbm=0&acr=1&ie=utf8&query={keyword}"
            full_url = f"https://ad.search.naver.com/search.naver?where=ad&query={keyword}"
            referer = "https://naver.com/"
            main_area_class = "api_subject_bx"
            full_area_class = "lst_type"
            name_tag = "span"
            class_name = "lnk_tit"

        headers = {
            'User-Agent': random.choice(headers_list),
            'Referer': referer,
            'Accept-Language': 'ko-KR,ko;q=0.8'
        }

        # -------------------------------
        # 1. 메인 광고 영역 탐색
        # -------------------------------
        try:
            soup = BeautifulSoup(requests.get(main_url, headers=headers).content, 'html.parser')
            found = False
            if environment == "mobile":
                ad_area = soup.find("ul", id="power_link_body", class_ ="lst_total")
                ad_items = ad_area.find_all("li", class_= ["bx","ext_law"]) if ad_area else []
                
                for idx, li in enumerate(ad_items, 1):
                    site = li.find("span", class_="tit")
                    if site and company_name in site.get_text(strip=True):
                        logger(f"  ✔ 메인 광고 노출 확인 (순위 {idx})")
                        results.append([keyword, 'Main', idx])
                        found = True
                        break
                
            else:
                ad_area = soup.find("div", id = "power_link_body", class_="nad_area")
                ad_items = ad_area.find_all("li",  class_=["lst", "type_more"]) if ad_area else []
                
                for idx, li in enumerate(ad_items, 1):
                    site = li.find("span", class_="lnk_tit")
                    if site and company_name in site.get_text(strip=True):
                            logger(f"  ✔ 메인 광고 노출 확인 (순위 {idx})")
                            results.append([keyword, 'Main', idx])
                            found = True
                            break

        except Exception as e:
            logger(f"  [에러] 메인 요청 실패: {e}")
            results.append([keyword, '', 'Error'])
            continue

        # -------------------------------
        # 2. 전체 광고 영역 탐색 (메인 실패 시)
        # -------------------------------
        if not found:
            logger("  ✖ 메인에서 발견 안 됨 → 전체 목록 검색 시도...")
            try:
                soup_all = BeautifulSoup(requests.get(full_url, headers=headers).content, 'html.parser')
                if environment == "mobile":
                    ad_area = soup_all.find("ol", class_="lst")
                    ad_items = ad_area.find_all("li", class_="lst") if ad_area else []
                    
                    for idx, li in enumerate(ad_items, 1):
                        site = li.find("span", class_="lnk_tit")
                        if site and company_name in site.get_text(strip=True):
                            logger(f"  ✔ 전체 목록 발견 (순위 {idx})")
                            results.append([keyword, 'All', idx])
                            found = True
                            break
                    
                else:
                    ad_area = soup_all.find("ol", class_="lst_type")
                    ad_items = ad_area.find_all("li", class_="lst") if ad_area else []
                    
                    for idx, li in enumerate(ad_items, 1):
                        site = li.find("span", class_="lnk_tit")
                        if site and company_name in site.get_text(strip=True):
                            logger(f"  ✔ 전체 목록 발견 (순위 {idx})")
                            results.append([keyword, 'All', idx])
                            found = True
                            break

                # for idx, li in enumerate(ad_items, 1):
                #     site = li.find(name_tag, class_=class_name)
                #     if site and company_name in site.get_text(strip=True):
                #         logger(f"  ✔ 전체 목록 발견 (순위 {idx})")
                #         results.append([keyword, 'All', idx])
                #         found = True
                #         break

                if not found:
                    logger("  ✖ 전체 목록에도 없음")
                    results.append([keyword, 'All', '<10'])

            except Exception as e:
                logger(f"  [에러] 전체 목록 요청 실패: {e}")
                results.append([keyword, 'All', 'Error'])

    return pd.DataFrame(results, columns=["키워드", "상위노출여부", "순위"])
