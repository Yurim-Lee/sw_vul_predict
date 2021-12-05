import pandas as pd
from sklearn.decomposition import TruncatedSVD
import numpy as np


# 취약점 순위 높은거 선정하는 함수
def vul_rank(input):
    # input : 프로그램 기능. 즉 label에 대한 데이터를(데이터프레임 형식의) 입력으로 주면 됨. ex) cal, mes, pay, res, cam
    tmp = input.sort_values(by=['aver_score'], axis=0, ascending=False)
    # print(tmp)
    c = 0
    for i in tmp['aver_score']:
        if i == 10.0:
            c += 1
    print("c = ", c)
    return tmp[:c]


def recom_sys(score, data, vul):
    # score : 최종적으로 사용할 점수 column 이름을 string 형식으로, 아직까지는 overall로 지정. 추후 점수 산정 방식이 변화하면 수정
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

print(result.shape)
print(result.head(3))
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

# == overall 대체 ====
"""
aver_list = []
for r in range(len(result)):
    tmp = result['exploitability'][r] + result['impact'][r] + result['base score'][r]
    aver_list.append(tmp)

result.insert(6, 'aver_score', aver_list)
"""
# == 새로 추가될 부분 ==============

tmp = vul_rank(cal)
print(tmp[:1]['SV name'])
vul_list = list(tmp['SV name'])
print(vul_list)

# == 새로 추가될 부분 ==============

corr_list = recom_sys("aver_score", result, vul_list[0])
print(len(corr_list))



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

