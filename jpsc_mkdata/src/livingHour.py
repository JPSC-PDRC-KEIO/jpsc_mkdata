# -*- coding: utf-8 -*-
# 通勤時間の調整(仕事・勉強時間の無い人)は、
# メッセージだけ表示させ、プログラム上での変更は行わない。


from numpy import *


def showHM(arg):
    # 何時何分表示”00:00”に変更
    r = ([str(int(x[0]) * 10 + int(x[1])) + ':' + x[2] + '0'
          if x != '999' else "0:00" for x in arg])
    return(r)


def commuteTime(arg):
    #
    caution = 0
    if arg[0] > 0 and (arg[1] == 0 and arg[2] == 0):
        caution = 1
    return(caution)


def toMinutes(arg):
    # 分表示に変更
    if arg == '999':
        ms = 0
    elif arg == '   ':
        ms = 0

    else:
        h = int(arg[0:2])
        m = int(arg[2])
        ms = h*60 + m*10

    return(ms)


def over24Each(arg):
    # 24時間以上の細目がある場合
    caution = 0
    a = array(arg)
    a[a == 999 * 60] = 0
    if sometrue(a >= 24 * 60):
        caution = 1
    return(caution)


def all0(arg):
    # 全ての時間が0分
    caution = 0
    a = array(arg)
    if all(a == 0):
        caution = 1
    return(caution)


def not24(arg):
    # 合計が24時間にならない
    # 関数over26 under22と合わせて使用
    caution = 0
    if sum(arg) != 24*60:
        caution = 1
    return(caution)


def over26(arg):
    # 合計が26時間を超える（調整をしない）
    caution = 0
    if sum(arg) > 26*60:
        caution = 1
    return(caution)


def under22(arg):
    # 合計が22時間未満（調整をしない）
    caution = 0
    if sum(arg) < 22 * 60:
        caution = 1
    return(caution)


def proration(arg):
    # 調整　24時間の超過、過小分を
    # (4)家事・育児,(5)趣味・娯楽、(6)睡眠・食事で比例配分
    # assert len(arg) != 6, "short of items"
    arg = [toMinutes(m) for m in arg]
    h = arg[3]+arg[4]+arg[5]
    r = sum(arg) - 24*60
    if h == 0:
        argR = ""
        argRM = ""
    else:
        hw = true_divide(arg[3], h) * r
        hby = true_divide(arg[4], h) * r
        slp = true_divide(arg[5], h) * r

        hw = round(hw/10)*10
        hby = round(hby/10)*10
        slp = round(slp/10)*10

        revise = [0, 0, 0, hw, hby, slp]

        argR = array(arg) - array(revise)
        if sum(argR) != 24*60:
            # 24時間との誤差がある場合、さらに睡眠・食事で調整
            rsd = sum(argR)-24*60
            argR = argR - array([0, 0, 0, 0, 0, rsd])
        hours = [int(floor(x)) for x in argR/60]
        minutes = [int(floor(x)) for x in argR % 60]

        argRM = \
            ([str(x[0])+':' + str(x[1] if x[1] != 0 else '00')
              for x in zip(hours, minutes)])

    #assert sum(argR)!=24*60,"not 1440"
    return argRM


def showAdjHour(arg1, arg2):
    # 調整する場合（今回は24±2）関数prorationを呼び出す
    adj = ''
    if arg1 == "合計が24時間にならない(24±2)":
        adj = proration(arg2)
    return adj


def checkHour(arg):
    fnc = [over24Each, all0, not24, over26, under22, commuteTime]
    argM = [toMinutes(m) for m in arg]
    # 無配偶の場合、夫が全て0になるため別処理
    isHsbnd = 1 if arg[0] == '   ' else 0
    check = [0]*len(fnc) if isHsbnd else [f(argM) for f in fnc]
    return(check)


def adjuster(arg):
    assert len(arg) != 7, "short of items"
    caution = ""
    a0 = arg[0]
    a1 = arg[1]
    a2 = arg[2]
    a3 = arg[3]
    a4 = arg[4]
    a5 = arg[5]

    if a0 == 1:
        caution = "24時間以上の項目あり"
    elif a1 == 1:
        caution = "すべてが999"
    elif a2 == 1 and (a0 != 1 or a1 != 1) and (a3 != 1 or a4 != 1):
        caution = "合計が24時間にならない(24±2)"

    # 24±2の場合、
    if a3 == 1 and a0 != 1 and a1 != 1:
        caution = "合計が26時間以上"
    if a4 == 1 and a0 != 1 and a1 != 1:
        caution = "合計が22時間以下"
    if a5 == 1:
        caution = caution + " 通勤通学の不整合"

    return(caution)


if __name__ == "__main__":

    with open("../data/fixed_width_data/p29_release/p28/p28_3.txt", "r") as fr:

        for i in fr:
            id = i[0:4]
            hasHsbnd = "有配偶" if(i[255:258] != '   ') else "無配偶"

            commute = i[177:180]
            work = i[180:183]
            study = i[183:186]
            houseWork = i[186:189]
            hobby = i[201:204]
            sleep = i[213:216]
            hourWife = [commute, work, study, houseWork, hobby, sleep]

            commuteHldy = i[216:219]
            workHldy = i[219:222]
            studyHldy = i[222:225]
            houseWorkHldy = i[225:228]
            hobbyHldy = i[240:243]
            sleepHldy = i[252:255]
            hourHldyWife = \
                [commuteHldy, workHldy, studyHldy,
                    houseWorkHldy, hobbyHldy, sleepHldy]

            commuteHsbnd = i[255:258]
            workHsbnd = i[258:261]
            studyHsbnd = i[261:264]
            houseWorkHsbnd = i[264:267]
            hobbyHsbnd = i[279:282]
            sleepHsbnd = i[291:294]
            hourHsbnd = \
                ([commuteHsbnd, workHsbnd, studyHsbnd, houseWorkHsbnd,
                  hobbyHsbnd, sleepHsbnd])

            commuteHldyHsbnd = i[294:297]
            workHldyHsbnd = i[297:300]
            studyHldyHsbnd = i[300:303]
            houseWorkHldyHsbnd = i[303:306]
            hobbyHldyHsbnd = i[318:321]
            sleepHldyHsbnd = i[330:333]
            hourHldyHsbnd = \
                ([commuteHldyHsbnd, workHldyHsbnd, studyHldyHsbnd,
                  houseWorkHldyHsbnd, hobbyHldyHsbnd, sleepHldyHsbnd])

            chk1 = checkHour(hourWife)
            chk2 = checkHour(hourHldyWife)
            chk3 = checkHour(hourHsbnd)
            chk4 = checkHour(hourHldyHsbnd)

            c1 = adjuster(chk1)
            c2 = adjuster(chk2)
            c3 = adjuster(chk3)
            c4 = adjuster(chk4)

            if len(c1+c2+c3+c4) != 0:
                # print('******************************')
                print(id, hasHsbnd)
                if c1 != '':
                    print("本人平日", c1)
                    print(showHM(hourWife))
                    print(showAdjHour(c1, hourWife))
                    print('')

                if c2 != '':
                    print("本人休日", c2)
                    print(showHM(hourHldyWife))
                    print(showAdjHour(c2, hourHldyWife))
                    print('')

                if c3 != '':
                    print("夫平日", c3)
                    print(showHM(hourHsbnd))
                    print(showAdjHour(c3, hourHsbnd))
                    print('')
                if c4 != '':
                    print("夫休日", c4)
                    print(showHM(hourHldyHsbnd))
                    print(showAdjHour(c4, hourHldyHsbnd))
                    print('')

            else:
                #print(id, hourWife, hourHldyWife, hourHsbnd, hourHldyHsbnd)
                pass
