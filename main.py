# Korean Stock Bot for Discord
# made by Alanimdeo(앨런임더#2043)

from ast import literal_eval
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, CommandNotFound
import json
import math
import pandas as pd
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
        now = str(datetime.today().year) + str(month).zfill(2) + str(day).zfill(2) + "235959"
        request = requests.get('https://finance.naver.com/item/sise_time.nhn?code=' + code + '&thistime=' + now, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'})
        soup = BeautifulSoup(request.text, 'html.parser')
        price = soup.find('span',class_='tah p11')
        if price == None:
            code = None
        else:
            price = int(str(price).replace('<span class="tah p11">','').replace('</span>','').replace(',',''))
        return name, code, price

sendMoneyCommand = ['보내기', '송금', 'ㅅㄱ', 'tr', 'send']
myStockCommand = ['내주식', '내', 'ㄵㅅ', 'ㄴㅈㅅ', 'ㄴ', 'swt', 's', 'my']
sellStockCommand = ['판매', 'ㅍㅁ', 'sell', 'va']
buyStockCommand = ['구매', 'ㄱㅁ', 'buy', 'ra']
selectAllCommand = ['전부', '모두', 'ㅈㅂ', 'ㅁㄷ', 'all', 'wq', 'ae']

@client.command() # test command
async def test(ctx, *content):
    print(type(ctx.author.id))

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
            await checkUser(ctx, lambda: sendMoney(ctx, content), None)
    except IndexError:
        await checkUser(ctx, lambda: showMoney(ctx, str(ctx.author.id)), None)

@client.command(aliases=['ㅈㅅ', 'wntlr', 'wt', 'stock'])
async def 주식(ctx, *content):
    try:
        content[0]
    except IndexError:
        await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='값을 입력하세요.'))
    else:
        if content[0] in myStockCommand:
            await checkUser(ctx, lambda: myStock(ctx, str(ctx.author.id), corpList), None)
        elif content[0] in buyStockCommand:
            await checkUser(ctx, lambda: buyStock(ctx, content), None)
        elif content[0] in sellStockCommand:
            await checkUser(ctx, lambda: sellStock(ctx, content), None)
        else:
            [name, code, price] = getNowPrice(content[0], corpList)
            if code == None:
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='%s 은(는) 존재하지 않는 기업입니다. 기업명을 올바르게 입력했는지, 대소문자를 구분하였는지 확인하세요.' % content[0]))
            else:
                await ctx.send(embed=discord.Embed(color=0x0090ff, title=":chart_with_upwards_trend: %s(%s)의 현재 주가" % (name, code), description="`%s원`" % format(int(price), ',')).set_image(url='https://ssl.pstatic.net/imgfinance/chart/item/area/day/%s.png?sidcode=%s' % (code, int(time.time() * 1000))).set_footer(text='차트 제공: 네이버 금융'))

@client.command(aliases=['한강물', 'ㅎㄱ', 'ㅎㄱㅁ', 'gksrkd', 'gksrkdanf', 'gr', 'gra'])
async def 한강(ctx, *content):
    request = requests.get('http://hangang.dkserver.wo.tc')
    await ctx.send(embed=discord.Embed(color=0x0067a3, title=':ocean: 현재 한강 수온', description='현재 한강의 수온은 `%s ℃` 입니다.\n\n자살 예방 핫라인 :telephone: 1577-0199\n희망의 전화 :telephone: 129' % literal_eval(request.text[1:])['temp']))

@client.command()
async def admin(ctx, *content):
    if ctx.author.id == 324101597368156161 or ctx.author.id == 828515050640637973:
        try:
            if content[0] == 'setMoney':
                userdata[content[1]]['money'] = int(content[2])
            elif content[0] == 'addMoney':
                userdata[content[1]]['money'] += int(content[2])
            elif content[0] == 'showStock':
                await myStock(ctx, content[1], corpList)
            elif content[0] == 'showMoney':
                await showMoney(ctx, content[1])
        except:
            pass
        finally:
            with open('./userdata.json', 'w') as json_file:
                json.dump(userdata, json_file, indent=4)
    else:
        await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='운영자가 아닙니다.'))

@client.event
async def checkUser(ctx, ifRegistered, ifNotRegistered):
    if str(ctx.author.id) in userdata:
        await ifRegistered()
    elif ifNotRegistered == None:
        await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 가입 필요', description='가입이 필요합니다. `%s가입`을 입력해 가입하세요.' % prefix))
    else:
        await ifNotRegistered()

async def register(ctx):
    userdata[str(ctx.author.id)] = {
        'money': 1000000,
        'stock': {}
    }
    with open('./userdata.json', 'w') as json_file:
        json.dump(userdata, json_file, indent=4)
    await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 가입 완료', description='가입이 완료되었습니다.'))

async def sendAlreadyRegisteredMessage(ctx):
    await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='이미 가입돼 있습니다.'))

async def showMoney(ctx, userID):
    stock = list(userdata[userID]['stock'].keys())
    stockValue = list(userdata[userID]['stock'].values())
    money = 0
    for i in range(len(userdata[userID]['stock'])):
        price = int(getNowPrice(stock[i], corpList)[2])
        money += price * stockValue[i]['amount']
    await ctx.send(embed=discord.Embed(color=0xffff00, title=':moneybag: %s 님의 돈' % ctx.author.display_name, description='현금: `%s원`\n주식: `%s원`\n주식 포함 금액: `%s원`' % (format(userdata[userID]['money'], ','), format(money, ','), format(userdata[userID]['money'] + money, ','))))

async def myStock(ctx, userID, df):
    stock = list(userdata[userID]['stock'].keys())
    stockValue = list(userdata[userID]['stock'].values())
    if len(stock) == 0:
        await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='보유한 주식이 없습니다.'))
    else:
        willSendMessage = ':information_source: %s 님의 주식 상태입니다.\n' % ctx.author.display_name
        for i in range(len(userdata[userID]['stock'])):
            [name, code, price] = getNowPrice(stock[i], corpList)
            if stockValue[i]['buyPrice'] > stockValue[i]['amount'] * price:
                willSendMessage += '```diff\n- %s(%s): %s주 (%s원)[%s원, -%s%%]```' % (name, code, format(int(stockValue[i]['amount']), ','), format(stockValue[i]['amount'] * price, ','), format(int(stockValue[i]['amount'] * price - stockValue[i]['buyPrice']), ','), round(float(stockValue[i]['buyPrice']) / float(stockValue[i]['amount'] * price) * 100 - 100, 2))
            elif stockValue[i]['buyPrice'] < stockValue[i]['amount'] * price:
                willSendMessage += '```diff\n+ %s(%s): %s주 (%s원))[+%s원, +%s%%]```' % (name, code, format(int(stockValue[i]['amount']), ','), format(stockValue[i]['amount'] * price, ','), format(int(stockValue[i]['amount'] * price - stockValue[i]['buyPrice']), ','), round(float(stockValue[i]['amount'] * price) / float(stockValue[i]['buyPrice']) * 100 - 100, 2))
            else:
                willSendMessage += '```yaml\n= %s(%s): %s주 (%s원)[=]```' % (name, code, format(int(stockValue[i]['amount']), ','), format(stockValue[i]['amount'] * price, ','))     
        await ctx.send(willSendMessage)

async def sendMoney(ctx, content):
    error = False
    try:
        targetUser = content[1].replace('<', '').replace('>', '').replace('@', '').replace('!', '')
        if len(targetUser) == 18:
            if userdata[str(ctx.author.id)]['money'] <= int(content[2]):
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='잔액이 부족합니다.'))
            elif int(content[2]) <= 0:
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='보낼 금액은 1원 이상이어야 합니다.'))
            else:
                await checkUser(ctx, lambda: sendMoney2(ctx, content, targetUser), lambda: ctx.send(embed=discord.Embed(color=0xff0000, name=':warning: 오류', description='받을 상대가 가입되어있지 않습니다.')))
        else:
            error = True
    except IndexError:
        print('IndexError')
        error = True
    except TypeError:
        print('TypeError')
        error = True
    finally:
        if error == True:
            await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='잘못된 양식입니다.\n양식: `%s돈 송금 <보낼 사람(멘션)> <액수>`' % prefix))

async def sendMoney2(ctx, content, targetUser):
    userdata[str(ctx.author.id)]['money'] += -int(content[2])
    userdata[targetUser]['money'] += int(content[2])
    with open('./userdata.json', 'w') as json_file:
        json.dump(userdata, json_file, indent=4)
    await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 송금 완료', description='송금을 완료했습니다.\n송금 후 잔액: `%s원`' % userdata[str(ctx.author.id)]['money']))

async def buyStock(ctx, content):
    success = False
    try:
        int(content[3])
    except ValueError:
        if content[3] in selectAllCommand:
            [name, code, price] = getNowPrice(content[2], corpList)
            content[3] = math.floor(userdata[str(ctx.author.id)]['money'] / price)
    finally:
        try:
            [name, code, price] = getNowPrice(content[2], corpList)
            buyPrice = int(content[3]) * price
            if code == None:
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='%s 은(는) 존재하지 않는 기업입니다. 기업명을 올바르게 입력했는지, 대소문자를 구분하였는지 확인하세요.' % content[2]))
            elif buyPrice <= 0:
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='수량은 0보다 커야 합니다.'))
            elif userdata[str(ctx.author.id)]['money'] < buyPrice:
                await ctx.send(embed=discord.Embed(color=0xffff00, title=':moneybag: 잔액 부족', description='가진 돈이 부족합니다.'))
            else:
                userdata[str(ctx.author.id)]['money'] += -buyPrice
                userdata[str(ctx.author.id)]['stock'][code]['amount'] += int(content[3])
                userdata[str(ctx.author.id)]['stock'][code]['buyPrice'] += buyPrice
                success = True
        except ValueError:
            await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='수량에는 숫자 또는 전부만 입력하세요.\n형식: `%s주식 구매 <기업명/종목코드> <수량/전부>`' % config['prefix']))
        except KeyError:
            userdata[str(ctx.author.id)]['stock'][code] = {
                'amount': int(content[3]),
                'buyPrice': buyPrice
            }
            success = True
        finally:
            if success == True:
                with open('./userdata.json', 'w') as json_file:
                    json.dump(userdata, json_file, indent=4)
                await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 구매 완료', description='%s(%s) 주식을 구매했습니다.\n구매 금액: `%s × %s = %s원`\n보유 중인 주식: `%s주`\n남은 돈: `%s원`' % (name, code, format(int(price), ','), format(int(content[3]), ','), format(int(price) * int(content[3]), ','), format(userdata[str(ctx.author.id)]['stock'][code]['amount'], ','), format(userdata[str(ctx.author.id)]['money'], ','))))

async def sellStock(ctx, content):
    try:
        int(content[2])
    except ValueError:
        if content[2] in selectAllCommand:
            code = getNowPrice(content[1], corpList)[1]
            content[2] = userdata[str(ctx.author.id)]['stock'][code]['amount']
    finally:
        try:
            int(content[2])
            [name, code, price] = getNowPrice(content[1], corpList)
            if code == None:
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='%s 은(는) 존재하지 않는 기업입니다. 기업명을 올바르게 입력했는지, 대소문자를 구분하였는지 확인하세요.' % content[1]))
            elif userdata[str(ctx.author.id)]['stock'][code]['amount'] < int(content[2]):
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='가진 주식보다 많이 판매할 수 없습니다.'))
            elif int(content[2]) <= 0:
                await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='수량은 0보다 커야 합니다.'))
            else:
                userdata[str(ctx.author.id)]['stock'][code]['amount'] += -int(content[2])
                userdata[str(ctx.author.id)]['stock'][code]['buyPrice'] += -(int(content[2]) * price)
                amount = userdata[str(ctx.author.id)]['stock'][code]['amount']
                if userdata[str(ctx.author.id)]['stock'][code]['amount'] == 0:
                    del userdata[str(ctx.author.id)]['stock'][code]
                    amount = 0
                userdata[str(ctx.author.id)]['money'] += int(content[2]) * price
                with open('./userdata.json', 'w') as json_file:
                    json.dump(userdata, json_file, indent=4)
                await ctx.send(embed=discord.Embed(color=0x008000, title=':white_check_mark: 판매 완료', description='%s(%s) 주식을 판매했습니다.\n판매 금액: `%s × %s = %s원`\n보유 중인 주식: `%s주`\n남은 돈: `%s원`' % (name, code, format(int(price), ','), format(int(content[2]), ','), format(int(price) * int(content[2]), ','), format(amount, ','), format(userdata[str(ctx.author.id)]['money'], ','))))
        except KeyError:
            await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='%s(%s)의 주식을 가지고 있지 않습니다.' % (name, code)))
        except ValueError as e:
            print(e)
            await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='수량에는 숫자 또는 전부만 입력하세요.\n형식: `%s주식 판매 <기업명/종목코드> <수량/전부>`' % config['prefix']))
        except IndexError:
            await ctx.send(embed=discord.Embed(color=0xff0000, title=':warning: 오류', description='값을 입력하세요.\n형식: `%s주식 판매 <기업명/종목코드> <수량/전부>`' % config['prefix']))

# Initialize
corpList = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0][['회사명', '종목코드']]
print('I\'m ready!\nToken: ' + config['token'])
client.run(config['token'])
