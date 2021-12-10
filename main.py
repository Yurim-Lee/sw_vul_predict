import pandas as pd
from sklearn.decomposition import TruncatedSVD
import numpy as np


# 취약점 순위 높은거 선정하는 함수
def vul_rank(input, en = 5):
    # input : 프로그램 기능. 즉 label에 대한 데이터를(데이터프레임 형식의) 입력으로 주면 됨. ex) cal, mes, pay, res, cam
    tmp = input.sort_values(by=['AY_score'], axis=0, ascending=False)
    tmp = tmp.drop_duplicates(['SV name'], keep='first')
    # print(tmp[:en])
    return tmp[:en]


def recom_sys(score, data, vul):
    # score : 최종적으로 사용할 점수 column 이름을 string 형식
    # data : 전체 데이터, 여기서는 result를 말함. DataFrame 구조로
    # vul : 취약점 string
    li_rating = data.pivot_table(score, index='label', columns='SV name')

    # print(il_rating)
    li_rating.fillna(0, inplace=True)
    il_rating = li_rating.values.T
    # print(il_rating.shape)

    SVD = TruncatedSVD(n_components=4)
    matrix = SVD.fit_transform(il_rating)
    # print(matrix.shape)

    corr = np.corrcoef(matrix)
    # print(corr.shape)

    cveid = li_rating.columns
    cveid_list = list(cveid)
    coffey_hands = cveid_list.index(vul)

    corr_ch = corr[coffey_hands]
    # print("print corr ch", corr_ch)
    corr_list = list(cveid[corr_ch >= 1])

    return corr_list


# label 0 = 'calendar' |  1 = 'messenger' |  2 = 'payment_service' |  3 = 'reservation_service' |  4 = 'camera'

cal = pd.read_csv("data/calendar.csv")
mes = pd.read_csv("data/messenger.csv")
pay = pd.read_csv("data/payment service.csv")
res = pd.read_csv("data/reservation service.csv")
cam = pd.read_csv("data/camera.csv")

# print("cal shape : ", cal.shape, cal.columns)
# print("mes shape : ", mes.shape, mes.columns)
# print("pay shape : ", pay.shape, pay.columns)
# print("res shape : ", res.shape, res.columns)
# print("cam shape : ", cam.shape, cam.columns)


li = ['cal', 'mes', 'pay', 'res', 'cam']
name_li = ['calendar', 'messenger', 'payment service', 'reservation service', 'camera']
num = 0

for n in range(5):
    aver_list = []
    for r in range(len(globals()['{}'.format(li[n])])):
        tmp = (globals()['{}'.format(li[n])]['exploitability'][r] + globals()['{}'.format(li[n])]['impact'][r] + globals()['{}'.format(li[n])]['base score'][r])/3
        aver_list.append(tmp)

    globals()['{}'.format(li[n])].insert(6, 'aver_score', aver_list)

for i in range(5):
    globals()['{}'.format(li[i])].drop('Unnamed: 0', axis = 1, inplace=True)
    globals()['{}'.format(li[i])].insert(6, 'label', name_li[num])
    num += 1

result = pd.concat([cal, mes], ignore_index=True)
result = pd.concat([result, pay], ignore_index=True)
result = pd.concat([result, res], ignore_index=True)
result = pd.concat([result, cam], ignore_index=True)

# print(result.shape)
# print(result.head(3))
# print(result.columns)

# type 확인
data_col = ['exploitability', 'impact', 'base score', 'overall']

for i in range(4):
    str_c = 0
    num_c = 0
    flo_c = 0
    elt = ""
    n = 0
    for j in result[data_col[i]]:
        if type(j) == type('a') :
            str_c += 1
            try:
                result[data_col[i]][n] = float(j)
            except:
                result[data_col[i]][n] = -0.1
        elif type(j) == type(1) :
            if j == 0:
                result[data_col[i]][n] = 0.00000000001
            num_c += 1
        elif type(j) == type(1.1):
            if j == 0.0:
                result[data_col[i]][n] = 0.00000000001
            flo_c += 1
        else:
            elt = type(j)
        n += 1

    # print("str : ", str_c, " num : ", num_c, "float : ", flo_c, 'else type : ', elt)

# == 새로 추가 - 년도별 가중치 =========
li2 = ['result', 'cal', 'mes', 'pay', 'res', 'cam']
tmp_list = []
for i in range(6):
    tlist = []
    for j in range(len(globals()['{}'.format(li2[i])])):
        c = 0
        test = globals()['{}'.format(li2[i])]['SV name'][j]
        test = int(test[4:8])
        score = (1-((2021 - test) * 0.01)) * globals()['{}'.format(li2[i])]['aver_score'][j]
        tlist.append(score)
    globals()['{}'.format(li2[i])].insert(6, 'AY_score', tlist)


# == 새로 추가될 부분 ==============
li = ['cal', 'mes', 'cam']
for j in range(3): # cal, mes, cam etc..  // 지금은 cal 기능으로 테스트
    tmp1 = vul_rank(globals()['{}'.format(li[j])])
    vul_list = list(tmp1['SV name'])
    for i in range(5): # vul list len -> 5
        corr_list = recom_sys("AY_score", result, vul_list[i])
        weight = 1 - (i * 0.005)
        # print("len list : ", len(corr_list))
        for k in range(len(corr_list)):
            a = result.loc[result['SV name'] == corr_list[k]]
            # df.at['Bob', 'age'] = 60

            a.at[a.index.values[0], 'AY_score'] = a['AY_score'] * weight
            if k == 0:
                clist = a
            else:
                clist = pd.concat([clist, a])
        if i == 0:
            rlist = vul_rank(clist)
        else:
            rlist = pd.concat([rlist, vul_rank(clist)])

# 최종
    concat_list = pd.concat([tmp1, rlist])
    result_list = vul_rank(concat_list, 10)
    comp_list = vul_rank(globals()['{}'.format(li[j])], 10)
    print("==============", li[j], "출력 ================\n\n")
    print("result : \n", result_list)
    print("비교 : \n", comp_list)
    print("\n\n")
    # 1. 상위권과의 차이점
    test_list = pd.concat([comp_list, result_list])
    print("원래 길이 : ", len(test_list))
    test_list = test_list.drop_duplicates(['SV name'], keep=False)
    print("겹치지 않는 길이 : ", len(test_list))

    # 2. 해당 데이터베이스에 있는지 비교
    count = 0

    # df.date.isin(['07311954'])
    na = list(result_list['SV name'])
    t = globals()['{}'.format(li[j])]['SV name'].isin(na)
    # print(t)
    for l in range(len(t)):
        if t[l] == True:
            count = count + 1

    print(len(result_list))
    print(li[j], "의 겹치는 값",count)




# 1. overall을 이용하면 전체적인 점수를 반영할 수 있을 것 같음
# 2. overall뿐만 아니라 다른 점수들을 서로 다른 가중치를 부여하여 overall과 같이 하나로 표현하여 나타내어도 괜찮을 것 같음
# 3. 해당 방식의 경우에는 비슷한 취약점을 뽑아내려면 취약점을 입력으로 주어야함. 우리가 생각했던 방식과는 다르기 때문에 다음과 같이 생각해볼 수 있을 것 같음
# # 3-1. 지금 여기에 나와있는 과정을 진행하기 앞서 원하는 '프로그램 기능'에 대한 주요 취약점 몇 가지(5가지 이상? 이 숫자는 논의해보면 좋을 것 같음)를 뽑아냄
# # 3-2. 해당 '프로그램 기능'에 대한 주요 취약점들과 관련성이 높은 취약점들을 뽑아냄.
# # 3-3. '프로그램 기능' 취약점과 그 취약점 관련 취약점을 비교함. 아마도 겹치는 값들도 있을텐데 그렇게 되면 그것은 순위를 좀 더 높이는 식으로 진행.
# # 3-4. 겹치지 않는 취약점이더라도 해당 방식과 얼마나 관련이 있는지와(관련도 점수를 이용, 여기에서는 corr_ch) 그 취약점이 가지고 있는 점수를 통해 순위를 계산하여 최종적으로 결과를 도출함
# # 3-5. 정리하면, 해당 '프로그램 기능'의 취약점과 이와 유사한 취약점들을 종합하여 순위를 다시 뽑아내어 이를 사용자에게 보여줌.
# # 3-6. 이를 통해서 사용자들에게 1차원적이 아닌 잠재적인 취약점까지 보여줄 수 있음.
# 4. overall 수정

# 현재 상태
# 프로그램 기능 관련 취약점 PV라고 하고, 취약점 관련 취약점을 VV라고 한다면,
# PV를 구하는 것은 완전히 구현, VV를 구하는 것은 일부만 진행
# VV를 구하는거를 일부만 한게 현재 캘린더의 경우에는 PV가 21개로 매우 많은 숫자가 나옴(전부 10점..)
# 이러한 문제로 PV 1개의 VV는 관련도를 1로 설정해두어도(최대치, 1 이상으로 높아질 수 없음 1~0사이의 소수값)300개가 넘는 숫자가 나옴
# 현재 이러한 문제를 해결하기 위해서 overall이 exploitability와 impact, base를 평균낸 값을 사용도 해보았지만 비슷한 결과를 보임..
# 따라서 PV와 VV에 영향을 줄 값을 하나 더 추가해야할 것으로 보임
# 이 값을 어떤 것을 사용할지 논의
# 추가로 VV를 구할 때 겹치는 값도 확인해볼 것인데 저거 다 해결되면..
# 참고로 cve id를 통해서 정보 가져오는 것 성공했음!! 코드는 별도로 존재하므로 따로 올려둘게

# 추가할 것
# 1. 점수에 데이터에서 해당 취약점이 발생하는 빈도에 따라 가중치 부여{5번 : 1, 4번 : 0.8, 3번 : 0.6, 2번 : 0.4, 1번 : 0.2}
# 1-1. 가중치에 대한 그래프를 통해 최적의 가중치를 선정해도 괜찮을듯?
# 1 --- 실패.. --- 전부 1개씩 존재함. 겹치지 않음.. 원래 이런건가..?
# 해당 방식은 label의 개수가 많아야지 사용 가능할 것 같음

# 2. 10 10 10 - 날짜 이용을 해서 구분
# 2-1. 2021 : 1 | 2020 : 0.99 | ...

# 3. VV에 대한 가중치 1순위 PV => 0.95, 2순위 PV => 0.9, 3순위 PV => 0.85, 4순위 PV => 0.8, 5순위 PV => 0.75

# 4. 최종 결과에서 중복된 값 제거하기

# 5. cal, mes, cam의 경우에는 최종 결과가 처음의 값과 완전히 똑같음.. 다른 두개는 개수가 적어서 그런지 오류가 발생하여서 일단 제외함.
# 6. 가중치 차이가 너무 큰 것으로 추측하여 가중치를 전반적으로 키우기로 함

# 궁금한 점(의아한 점)
# 추천시스템이 원래 실행할 때마다 달라지는게 맞는건가?

# 향후 계획 -> 해당 가중치를 딥러닝을 이용하여 학습 + 데이터셋을 더욱 방대하게 구축하여 많은 경우를 포함할 수 있도록함 + 추가로 프로그램 기능들 끼리의 유사성도 체크(현재 그 부분까지는 진행하지 못하였음)
# 여기에 위에서 중복되는 값을 그냥 제거했는데 추가적으로 값을 더해주는 방식으로 진행해도 될 것 같음
# 현재 중복되는 값에 값을 추가하지 못한 이유는 중복된 이유를 명확하게 확인하지 못하였기 때문..
