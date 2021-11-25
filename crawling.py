
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

#url 접속 - 취약점 누르기 - 점수 나오는 페이지로 이동 - 점수 가져오기 - url 다시 접속 - 다음 취약점 누르기 - 점수 페이지 ... - 다음 페이지 url 접속
driver = webdriver.Chrome()

keyword = 'camera'

vul_name = []
exploitability = []
impact = []
basescore = []
overall = []


for i in range(0,760,20):#640, 20):#200, 20): #i는 0,20,... 각 페이지의 시작 인덱스
    #200까지 먼저 하고 뒤에 더 해서 추가하기
    url = 'https://nvd.nist.gov/vuln/search/results?isCpeNameSearch=false&query=' + keyword + '&results_type=overview&form_type=Basic&search_type=all&startIndex=' + str(i)
    driver.get(url)
    print("URL 접속 완")
    for j in range(1,21): #j는 각 페이지에서 몇번째 취약점인지. 1부터 20까지
        try:
            bt1_path = '//*[@id="row"]/table/tbody/tr[' + str(j) + ']/th/strong/a'
            bt1 = driver.find_element(By.XPATH, bt1_path)
            bt1.click()
            print("1번 버튼1 완료")
            try:
                bt = driver.find_element(By.XPATH, '//*[@id="btn-cvss2"]')
                bt.click()

                time.sleep(1)

                bt2 = driver.find_element(By.XPATH, '//*[@id="Cvss2CalculatorAnchor"]')
                bt2.click()
                print("1번 버튼2 try")

                time.sleep(2)
                exploit = driver.find_element(By.XPATH, '// *[ @ id = "cvss-exploitability-score-cell"]').text
                impact1 = driver.find_element(By.XPATH, '// *[ @ id = "cvss-impact-score-cell"]').text
                base = driver.find_element(By.XPATH, '// *[ @ id = "cvss-base-score-cell"]').text
                vul = driver.find_element(By.XPATH, '//*[@id="CvssHeaderText"]/a').text
                over = driver.find_element(By.XPATH, '//*[@id="cvss-overall-score-cell"]').text

                print("base ", base)
                vul_name.append(vul)
                exploitability.append(exploit)
                impact.append(impact1)
                basescore.append(base)
                overall.append(over)

            except Exception as error:
                exploit = 'NO'
                impact1 = 'NO'
                base = 'NO'
        except Exception as error:
            print("버튼 1 에러 발생")
        time.sleep(5)
        url = 'https://nvd.nist.gov/vuln/search/results?isCpeNameSearch=false&query=' + keyword + '&results_type=overview&form_type=Basic&search_type=all&startIndex=' + str(i)
        driver.get(url)


print("vul name: ", vul_name)
print("exploitability: ", exploitability)
print("impact: ", impact)
print("base score: ", basescore)
print("overall: ", overall)
