# Korean Stock Bot for Discord
# made by Alanimdeo(앨런임더#2043)

from ast import literal_eval
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, CommandNotFound
from discord.utils import get
import json
import math
import pandas as pd
import random
import re
import requests
import time

with open('./userdata.json', 'r') as json_file:
    userdata = json.load(json_file)

with open('./config.json', "r") as json_file:
    config = json.load(json_file)
    prefix = config['prefix']

client = commands.Bot(command_prefix=prefix)
client.remove_command('help')


def getNowPrice(name, df):
    try:
        code = str(int(name))
    except ValueError:
        code = str(df[df.회사명 == name].종목코드.values)[1:-1].zfill(6)
    else:
        code = code.zfill(6)
        name = str(df[df.종목코드 == int(code.lstrip("0"))].회사명.values)[2:-2]
    finally:
        year = datetime.today().year
        day = datetime.today().day
        month = datetime.today().month
        if datetime.today().weekday() == 5:
            day += -1
        elif datetime.today().weekday() == 6:
            day += -2
        elif datetime.today().hour < 9:
            if datetime.today().weekday() == 0:
                day += -2
            day += -1
        if day < 1:
            month += -1
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day = 31
            elif month in [4, 6, 9, 11]:
                day = 30
            elif month == 2:
                day = 29
        if month == 0:
            month = 12
            year += -1
            day = 31
        now = str(year) + str(month).zfill(2) + str(day).zfill(2) + "235959"
        request = requests.get('https://finance.naver.com/item/sise_time.nhn?code=' + code + '&thistime=' + now, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'})
        soup = BeautifulSoup(request.text, 'html.parser')
        price = soup.find('span', class_='tah p11')
        if price == None:
            code = None
        else:
            price = int(str(price).replace('<span class="tah p11">','').replace('</span>', '').replace(',', ''))
        return name, code, price


sendMoneyCommand = ['보내기', '송금', 'ㅅㄱ', 'tr', 'send']
myStockCommand = ['내주식', '내', 'ㄵㅅ', 'ㄴㅈㅅ', 'ㄴ', 'swt', 's', 'my']
sellStockCommand = ['판매', 'ㅍㅁ', 'sell', 'va']
buyStockCommand = ['구매', 'ㄱㅁ', 'buy', 'ra']
selectAllCommand = ['전부', '모두', 'ㅈㅂ', 'ㅁㄷ', 'all', 'wq', 'ae']
checkLotteryCommand = ['확인', 'ㅎㅇ', 'gr', 'check']
lotteryNumberCommand = ['번호', 'ㅂㅎ', 'qg', 'number']
latestLotteryCommand = ['최신', '현재', 'ㅊㅅ', 'ㅎㅈ', 'ct', 'gw', 'now', 'latest']
lotteryAutoCommand = ['자동', 'ㅈㄷ', 'auto', 'we']


@client.command(aliases=['도움', '명령어', '커맨드', 'help', 'command', 'commands'])
async def 도움말(ctx, *content):
    await ctx.send(embed=discord.Embed(color=0x0067a3, title=':information_source: 도움말 확인', description='자세한 설명은 [이곳](<https://stockbot.alan.imdeo.kr/>)에서 보실 수 있습니다.'))


@client.command(aliases=['ㄱㅇ', 'join', 'register'])
async def 가입(ctx, *content):
    await checkUser(ctx, lambda: sendAlreadyRegisteredMessage(ctx), lambda: register(ctx))


@client.command(aliases=['ㄷ', 'ehs', 'e', 'money'])
async def 돈(ctx, *content):
    try:
        if content[0] in sendMoneyCommand:
            await checkUser(ctx, lambda: sendMoney(ctx, content))
    except IndexError:
        await checkUser(ctx, lambda: showMoney(ctx, str(ctx.author.id)))


@client.command(aliases=['ㅈㅅ', 'wntlr', 'wt', 'stock'])
async def 주식(ctx, *content):
    try:
        if content[0] in myStockCommand:
            await checkUser(ctx, lambda: myStock(ctx, str(ctx.author.id), corpList))
        elif content[0] in buyStockCommand:
            await checkUser(ctx, lambda: buyStock(ctx, content))
        elif content[0] in sellStockCommand:
            await checkUser(ctx, lambda: sellStock(ctx, content))
        else:
            [name, code, price] = getNowPrice(content[0], corpList)
            if code == None:
                await raiseError(ctx, '%s 은(는) 존재하지 않는 기업입니다. 기업명을 올바르게 입력했는지, 대소문자를 구분하였는지 확인하세요.' % content[0])
            else:
                await ctx.send(embed=discord.Embed(color=0x0090ff, title=":chart_with_upwards_trend: %s(%s)의 현재 주가" % (name, code), description="`%s원`" % format(int(price), ',')).set_image(url='https://ssl.pstatic.net/imgfinance/chart/item/area/day/%s.png?sidcode=%s' % (code, int(time.time() * 1000))).set_footer(text='차트 제공: 네이버 금융'))
    except IndexError:
        await raiseError(ctx, '형식에 맞게 명령어를 입력하세요.\n주가 확인: `%s주식 [기업명]`\n내 주식 확인: `%s주식 내주식`\n구매: `%s주식 구매 [기업명] [수량]`\n판매: `%s주식 판매 [기업명] [수량]`' % (prefix, prefix, prefix))


@client.command(aliases=['한강물', 'ㅎㄱ', 'ㅎㄱㅁ', 'gksrkd', 'gksrkdanf', 'gr', 'gra'])
async def 한강(ctx):
    request = requests.get('http://hangang.dkserver.wo.tc')
    await ctx.send(embed=discord.Embed(color=0x0067a3, title=':ocean: 현재 한강 수온', description='현재 한강의 수온은 `%s ℃` 입니다.\n\n자살 예방 핫라인 :telephone: 1577-0199\n희망의 전화 :telephone: 129' % literal_eval(request.text[1:])['temp']))


@client.command(aliases=['돈받기', 'ㄷㅂㄱ', 'eqr'])
async def 용돈(ctx):
    nowtime = time.localtime(time.time())
    if userdata[str(ctx.author.id)]['lastClaim'] == [nowtime.tm_year, nowtime.tm_yday]:
        await raiseError(ctx, '오늘 용돈을 이미 받으셨습니다. 내일 다시 시도하세요.')
    else:
        money = round(random.randrange(2000, 5001), -2)
        userdata[str(ctx.author.id)]['lastClaim'] = [nowtime.tm_year, nowtime.tm_yday]
        userdata[str(ctx.author.id)]['money'] += money
        await ctx.send(embed=discord.Embed(color=0x008000, title=':money_with_wings: 오늘의 용돈', description='오늘 용돈으로 `%s원`을 받았습니다.\n 현재 잔액: `%s원`' % (format(money, ','), format(userdata[str(ctx.author.id)]['money'], ','))))
        updateUserdata()
        
def findDrwNo():
    drwNo = (int(time.time()) - 1038582000) / 604800 # 회차
    nowtime = time.localtime(time.time())
    if nowtime.tm_wday == 5:
        if int(str(nowtime.tm_hour) + str(nowtime.tm_min)) < 2045: # 토요일 20시 45분(로또 추첨 시간) 이전
            return int(drwNo - 1)
    else:
        return int(drwNo)

def getLotto(drwNo):
    return literal_eval(requests.get('https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=' + str(drwNo)).text)



@client.command(aliases=['복권', 'lotto'])
async def 로또(ctx, *content):
    try:
        if content[0] in buyStockCommand:
            currentDrwNo = findDrwNo() + 1
            currentDrwAmount = 0
            for lottery in userdata[str(ctx.author.id)]['lottery']:
                if lottery['drwNo'] == currentDrwNo:
                    currentDrwAmount += 1
            if currentDrwAmount == 100:
                await ctx.send(embed=discord.Embed(color=0xffff00, title=':warning: 구매 한도 도달', description='회차당 최대 5게임까지 구매 가능합니다.\n\n한국도박문제 관리센터: :telephone: 1336'))
            else:
                if content[1] in lotteryAutoCommand:
                    numbers = []
                    while len(numbers) < 6:
                        queue = random.randint(1, 45)
                        if queue not in numbers:
                            numbers.append(queue)
                else:
                    numbers = []
                    for queue in list(map(int, content[1:7])):
                        if queue in numbers:
                            await raiseError(ctx, '같은 번호를 여러 개 입력하실 수 없습니다.')
                            return
                        elif queue < 1 or queue > 45:
                            await raiseError(ctx, '로또 번호는 1부터 45까지 입력 가능합니다.')
                            return
                        else:
                            numbers.append(queue)
                userdata[str(ctx.author.id)]['lottery'].append({'drwNo': currentDrwNo, 'numbers': numbers})
                userdata[str(ctx.author.id)]['money'] -= 1000
                updateUserdata()
                await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 구매 완료', description='로또를 구매했습니다.\n회차: %s회\n번호: **%s %s %s %s %s %s**' % (currentDrwNo, numbers[0], numbers[1], numbers[2], numbers[3], numbers[4], numbers[5])))
        elif content[0] in checkLotteryCommand:
            if len(userdata[str(ctx.author.id)]['lottery']) == 0:
                await raiseError(ctx, '가진 로또가 없습니다.')
            else:
                currentDrwNo = findDrwNo()
                shouldDelete = []
                msg = ':information_source: %s 님이 보유한 로또 목록입니다.' % ctx.author
                for index, lottery in enumerate(userdata[str(ctx.author.id)]['lottery']):
                    correctAmount = 0
                    lotto = getLotto(lottery['drwNo'])
                    if lotto['returnValue'] == 'success':
                        r = requests.post('https://www.dhlottery.co.kr/gameResult.do?method=byWin', data = {'drwNo': lottery['drwNo']})
                        soup = BeautifulSoup(r.text, 'html.parser')
                        money = soup.find_all('td', class_='tar')
                        firstMoney = re.split('<|>', str(money[1]))[2]
                        secondMoney = re.split('<|>', str(money[3]))[2]
                        thirdMoney = re.split('<|>', str(money[5]))[2]
                        shouldDelete.append(index)
                        for i in range(1, 7):
                            if lotto['drwtNo%s' % i] in lottery['numbers']:
                                correctAmount += 1
                        if lotto['bnusNo'] in lottery['numbers']:
                            isBonus = True
                        else:
                            isBonus = False
                        if correctAmount < 3:
                            lottoHead = 'diff\n-'
                            prize = '(낙첨)'
                        else:
                            lottoHead = 'diff\n+'
                            if correctAmount == 3:
                                prize = '(5등, 5,000원)'
                                userdata[str(ctx.author.id)]['money'] += 5000
                            elif correctAmount == 4:
                                prize = '(4등, 50,000원)'
                                userdata[str(ctx.author.id)]['money'] += 50000
                            elif correctAmount == 5 and not isBonus:
                                prize = '(3등, %s)' % thirdMoney
                                userdata[str(ctx.author.id)]['money'] += int(thirdMoney.replace(',', '')[0:-1])
                            elif correctAmount == 5 and isBonus:
                                prize = '(2등, %s)' % secondMoney
                                userdata[str(ctx.author.id)]['money'] += int(secondMoney.replace(',', '')[0:-1])
                            elif correctAmount == 6:
                                prize = '(1등, %s)' % firstMoney
                                userdata[str(ctx.author.id)]['money'] += int(firstMoney.replace(',', '')[0:-1])
                    else:
                        lottoHead = '\n*'
                        prize = '(추첨 전)'
                    msg += '```%s %s회차 | %s %s %s %s %s %s %s```' % (lottoHead, lottery['drwNo'], lottery['numbers'][0], lottery['numbers'][1], lottery['numbers'][2], lottery['numbers'][3], lottery['numbers'][4], lottery['numbers'][5], prize)
                for i in shouldDelete:
                    userdata[str(ctx.author.id)]['lottery'][i] = 'deleted'
                while 'deleted' in userdata[str(ctx.author.id)]['lottery']:
                    userdata[str(ctx.author.id)]['lottery'].remove('deleted')
                updateUserdata()
                await ctx.send(msg)
        elif content[0] in lotteryNumberCommand:
            if content[1] in latestLotteryCommand:
                drwNo = findDrwNo()
            else:
                drwNo = content[1]
            lotto = getLotto(int(drwNo))
            if lotto['returnValue'] == 'success':
                await ctx.send(embed=discord.Embed(color=0x008000, title=':slot_machine: %s회차(%s) 로또 6/45 당첨번호' % (lotto['drwNo'], lotto['drwNoDate']), description='**%s %s %s %s %s %s + %s**\n1등 당첨자 수: %s명\n1등 당첨금: %s원' % (lotto['drwtNo1'], lotto['drwtNo2'], lotto['drwtNo3'], lotto['drwtNo4'], lotto['drwtNo5'], lotto['drwtNo6'], lotto['bnusNo'], format(lotto['firstPrzwnerCo'], ','), format(lotto['firstWinamnt'], ','))))
            else:
                await raiseError(ctx, '아직 추첨이 진행되지 않았습니다.\n정규 추첨 시간: 매주 토요일 오후 8:45분')
    except:
        await raiseError(ctx, '형식에 맞게 명령어를 입력하세요.\n구매: `%s로또 구매 자동/[번호1 번호2 번호3 번호4 번호5 번호6]`\n당첨 확인: `%s로또 확인`\n번호 확인: `%s로또 번호 최신/[회차 번호]`' % (prefix, prefix, prefix))

@client.command()
async def admin(ctx, *content):
    if ctx.author.id == 324101597368156161 or ctx.author.id == 828515050640637973:
        if content[0] == 'setMoney':
            userdata[content[1]]['money'] = int(content[2])
        elif content[0] == 'addMoney':
            userdata[content[1]]['money'] += int(content[2])
        elif content[0] == 'showStock':
            await myStock(ctx, content[1], corpList)
        elif content[0] == 'showMoney':
            await showMoney(ctx, content[1])
        elif content[0] == 'addStock':
            userdata[content[1]]['stock'][content[2]]['amount'] += int(content[3])
        elif content[0] == 'setStock':
            userdata[content[1]]['stock'][content[2]]['amount'] = int(content[3])
        elif content[0] == 'resetClaim':
            userdata[content[1]]['lastClaim'] = [0, 0]
        elif content[0] == 'shutdown':
            exit()
        updateUserdata()
    else:
        await raiseError(ctx, '운영자가 아닙니다.')


@client.event
async def raiseError(ctx, msg):
    await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description=msg))


async def checkUser(ctx, ifRegistered, ifNotRegistered=None):
    if str(ctx.author.id) in userdata:
        await ifRegistered()
    elif ifNotRegistered == None:
        await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 가입 필요', description='가입이 필요합니다. `%s가입`을 입력해 가입하세요.' % prefix))
    else:
        await ifNotRegistered()


async def register(ctx):
    userdata[str(ctx.author.id)] = {
        'money': 1000000,
        'stock': {},
        'lottery': [],
        'lastClaim': [0, 0]
    }
    updateUserdata()
    await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 가입 완료', description='가입이 완료되었습니다.'))


async def sendAlreadyRegisteredMessage(ctx):
    await raiseError(ctx, '이미 가입돼 있습니다.')


async def showMoney(ctx, userID):
    user = await ctx.message.guild.fetch_member(int(userID))
    stock = list(userdata[userID]['stock'].keys())
    stockValue = list(userdata[userID]['stock'].values())
    money = 0
    for i in range(len(userdata[userID]['stock'])):
        price = getNowPrice(stock[i], corpList)[2]
        if price != None:
            money += int(price) * stockValue[i]['amount']
    await ctx.send(embed=discord.Embed(color=0xffff00, title=':moneybag: %s 님의 돈' % user.display_name, description='현금: `%s원`\n주식: `%s원`\n주식 포함 금액: `%s원`' % (format(userdata[userID]['money'], ','), format(money, ','), format(userdata[userID]['money'] + money, ','))))


async def myStock(ctx, userID, df):
    user = await ctx.message.guild.fetch_member(int(userID))
    stock = list(userdata[userID]['stock'].keys())
    stockValue = list(userdata[userID]['stock'].values())
    if len(stock) == 0:
        await raiseError(ctx, '보유한 주식이 없습니다.')
    else:
        willSendMessage = ':information_source: %s 님의 주식 상태입니다.\n' % user.display_name
        for i in range(len(userdata[userID]['stock'])):
            [name, code, price] = getNowPrice(stock[i], corpList)
            if price == None:
                willSendMessage += '```\n* %s(%s): %s주 (평균 구매가 %s원, 현재 거래정지 상태)```' % (name, code, format(int(stockValue[i]['amount']), ',').replace('.0', ''), format(math.floor(stockValue[i]['buyPrice'] / stockValue[i]['amount']), ',').replace('.0', ''))
            elif stockValue[i]['buyPrice'] > stockValue[i]['amount'] * price:
                willSendMessage += '```diff\n- %s(%s): %s주 (평균 구매가 %s원, 현재 %s원)[%s원, -%s%%]```' % (name, code, format(int(stockValue[i]['amount']), ',').replace('.0', ''), format(math.floor(stockValue[i]['buyPrice'] / stockValue[i]['amount']), ',').replace('.0', ''), format(price, ','), format(int(stockValue[i]['amount'] * price - stockValue[i]['buyPrice']), ','), round(float(stockValue[i]['buyPrice']) / float(stockValue[i]['amount'] * price) * 100 - 100, 2))
            elif stockValue[i]['buyPrice'] < stockValue[i]['amount'] * price:
                willSendMessage += '```diff\n+ %s(%s): %s주 (평균 구매가 %s원, 현재 %s원)[+%s원, +%s%%]```' % (name, code, format(int(stockValue[i]['amount']), ',').replace('.0', ''), format(math.floor(stockValue[i]['buyPrice'] / stockValue[i]['amount']), ',').replace('.0', ''), format(price, ','), format(int(stockValue[i]['amount'] * price - stockValue[i]['buyPrice']), ','), round(float(stockValue[i]['amount'] * price) / float(stockValue[i]['buyPrice']) * 100 - 100, 2))
            else:
                willSendMessage += '```yaml\n= %s(%s): %s주 (평균 구매가 %s원, 현재 %s원)[=]```' % (name, code, format(int(stockValue[i]['amount']), ',').replace('.0', ''), format(math.floor(stockValue[i]['buyPrice'] / stockValue[i]['amount']), ',').replace('.0', ''), format(price, ','))
        await ctx.send(willSendMessage)


async def sendMoney(ctx, content):
    try:
        targetUser = content[1].replace('<', '').replace('>', '').replace('@', '').replace('!', '')
        if len(targetUser) == 18:
            if userdata[str(ctx.author.id)]['money'] <= int(content[2]):
                await raiseError(ctx, '잔액이 부족합니다.')
            elif int(content[2]) <= 0:
                await raiseError(ctx, '보낼 금액은 1원 이상이어야 합니다.')
            else:
                await checkUser(ctx, lambda: sendMoney2(ctx, content, targetUser), lambda: ctx.send(embed=discord.Embed(color=0xff0000, name=':warning: 오류', description='받을 상대가 가입되어있지 않습니다.')))
        else:
            raise Exception()
    except:
        await raiseError(ctx, '잘못된 양식입니다.\n양식: `%s돈 송금 <보낼 사람(멘션)> <액수>`' % prefix)


async def sendMoney2(ctx, content, targetUser):
    user = await ctx.message.guild.fetch_member(int(targetUser))
    userdata[str(ctx.author.id)]['money'] += -int(content[2])
    userdata[targetUser]['money'] += int(content[2])
    updateUserdata()
    await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 송금 완료', description='%s 님께 송금을 완료했습니다.\n송금 후 잔액: `%s원`' % (user.display_name, userdata[str(ctx.author.id)]['money'])))


async def buyStock(ctx, content):
    success = False
    buyAmount = ''
    try:
        int(content[2])
    except ValueError:
        if content[2] in selectAllCommand:
            [name, code, price] = getNowPrice(content[1], corpList)
            buyAmount = math.floor(
                userdata[str(ctx.author.id)]['money'] / price)
    else:
        buyAmount = content[2]
    finally:
        try:
            [name, code, price] = getNowPrice(content[1], corpList)
            buyPrice = int(buyAmount) * price
            if code == None:
                await raiseError(ctx, '%s 은(는) 존재하지 않는 기업입니다. 기업명을 올바르게 입력했는지, 대소문자를 구분하였는지 확인하세요.' % content[1])
            elif buyPrice <= 0:
                await raiseError(ctx, '수량은 0보다 커야 합니다.')
            elif userdata[str(ctx.author.id)]['money'] < buyPrice:
                await ctx.send(embed=discord.Embed(color=0xffff00, title=':moneybag: 잔액 부족', description='가진 돈이 부족합니다.'))
            else:
                userdata[str(ctx.author.id)]['money'] += -buyPrice
                userdata[str(ctx.author.id)]['stock'][code]['amount'] += int(buyAmount)
                userdata[str(ctx.author.id)]['stock'][code]['buyPrice'] += buyPrice
                success = True
        except ValueError:
            await raiseError(ctx, '수량에는 숫자 또는 전부만 입력하세요.\n형식: `%s주식 구매 <기업명/종목코드> <수량/전부>`' % config['prefix'])
        except KeyError:
            userdata[str(ctx.author.id)]['stock'][code] = {
                'amount': int(buyAmount),
                'buyPrice': buyPrice
            }
            success = True
        finally:
            if success == True:
                updateUserdata()
                await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 구매 완료', description='%s(%s) 주식을 구매했습니다.\n구매 금액: `%s × %s = %s원`\n보유 중인 주식: `%s주`\n남은 돈: `%s원`' % (name, code, format(int(price), ','), format(int(buyAmount), ','), format(int(price) * int(buyAmount), ','), format(userdata[str(ctx.author.id)]['stock'][code]['amount'], ','), format(userdata[str(ctx.author.id)]['money'], ','))))


async def sellStock(ctx, content):
    sellAmount = ''
    try:
        int(content[2])
    except ValueError:
        if content[2] in selectAllCommand:
            code = getNowPrice(content[1], corpList)[1]
            sellAmount = userdata[str(ctx.author.id)]['stock'][code]['amount']
    else:
        sellAmount = content[2]
    finally:
        try:
            [name, code, price] = getNowPrice(content[1], corpList)
            if code == None:
                await raiseError(ctx, '%s 은(는) 존재하지 않는 기업입니다. 기업명을 올바르게 입력했는지, 대소문자를 구분하였는지 확인하세요.' % content[1])
            elif userdata[str(ctx.author.id)]['stock'][code]['amount'] < int(sellAmount):
                await raiseError(ctx, '가진 주식보다 많이 판매할 수 없습니다.')
            elif int(sellAmount) <= 0:
                await raiseError(ctx, '수량은 0보다 커야 합니다.')
            else:
                userdata[str(ctx.author.id)]['stock'][code]['amount'] += -int(sellAmount)
                userdata[str(ctx.author.id)]['stock'][code]['buyPrice'] += - \
                    (int(sellAmount) * price)
                amount = userdata[str(ctx.author.id)]['stock'][code]['amount']
                if userdata[str(ctx.author.id)]['stock'][code]['amount'] == 0:
                    del userdata[str(ctx.author.id)]['stock'][code]
                    amount = 0
                userdata[str(ctx.author.id)
                         ]['money'] += int(sellAmount) * price
                updateUserdata()
                await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 판매 완료', description='%s(%s) 주식을 판매했습니다.\n판매 금액: `%s × %s = %s원`\n보유 중인 주식: `%s주`\n남은 돈: `%s원`' % (name, code, format(int(price), ','), format(int(sellAmount), ','), format(int(price) * int(sellAmount), ','), format(amount, ','), format(userdata[str(ctx.author.id)]['money'], ','))))
        except KeyError:
            await raiseError(ctx, '%s(%s)의 주식을 가지고 있지 않습니다.' % (name, code))
        except ValueError as e:
            print(e)
            await raiseError(ctx, '수량에는 숫자 또는 전부만 입력하세요.\n형식: `%s주식 판매 <기업명/종목코드> <수량/전부>`' % config['prefix'])
        except IndexError:
            await raiseError(ctx, '값을 입력하세요.\n형식: `%s주식 판매 <기업명/종목코드> <수량/전부>`' % config['prefix'])


def updateUserdata():
    with open('./userdata.json', 'w') as json_file:
        json.dump(userdata, json_file, indent=4)


# Initialize
corpList = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0][['회사명', '종목코드']]
print('I\'m ready!\nToken: ' + config['token'])
client.run(config['token'])
