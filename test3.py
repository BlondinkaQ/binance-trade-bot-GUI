import asyncio
from tkinter import *
from tkinter import ttk
from binance import AsyncClient, BinanceSocketManager
from datetime import datetime, timedelta
from binance.client import Client


api_key = 'xsB5mdl4aNvyWlOlByBO8VmThW5EI3b81MGNXq6TTpEwZ5PYRjedxzM7S8DN4CPd'
api_secret_key = 'vSkMlwg8OGDm0UFdkYa2rYWUnYEh0RsrqspAn5BZctprCmTWGy3MFtgOfeqsB0q6'

async def main():
    def datetime_range(start, end, delta):
        current = start
        while current < end:
            yield current
            current += delta


    async def kline_listener():
        client = await AsyncClient.create(api_key, api_secret_key)
        client.API_URL = 'https://testnet.binance.vision/api'
        bm = BinanceSocketManager(client)

        global block_all
        block_all = False
        async with bm.kline_socket(symbol='BTCUSDT', interval='5m') as stream:
            data_check_buy = []
            while True:
                res = await stream.recv()

                date_kyiv_not_formated = datetime.fromtimestamp(int(res['E']) // 1000)
                date_not_formated_year = datetime.fromtimestamp(int(res['E']) / 1000).year
                date_not_formated_month = datetime.fromtimestamp(int(res['E']) / 1000).month
                date_not_formated_day = datetime.fromtimestamp(int(res['E']) / 1000).day
                date_not_formated_hour = datetime.fromtimestamp(int(res['E']) / 1000).hour
                if date_not_formated_hour == 23:
                    dts = [dt for dt in datetime_range(
                               datetime(date_not_formated_year, date_not_formated_month, date_not_formated_day,
                                        date_not_formated_hour),
                               datetime(date_not_formated_year, date_not_formated_month, date_not_formated_day + 1,
                                        0, 1),
                               timedelta(minutes=5))]
                else:
                    dts = [dt for dt in
                           datetime_range(
                               datetime(date_not_formated_year, date_not_formated_month, date_not_formated_day,
                                        date_not_formated_hour),
                               datetime(date_not_formated_year, date_not_formated_month, date_not_formated_day,
                                        date_not_formated_hour + 1, 1),
                               timedelta(minutes=5))]


                if block_all == True:
                    print('yes')

                    btccoin = float(e1.get().replace(',','.'))
                    if e2.get() == '':
                        up_ma = 0
                    else:
                        up_ma = float(e2.get().replace(',','.'))

                    if e3.get() == '':
                        down_ma = 0
                    else:
                        down_ma = float(e3.get().replace(',','.'))


                    print(btccoin)
                    print(up_ma)
                    print(down_ma)

                    e1.config(state = DISABLED)
                    e2.config(state = DISABLED)
                    e3.config(state = DISABLED)
                    button_order.config(state=DISABLED)

                    if data_check_buy == []:
                        info_order = 'NO DATA ORDER'
                    elif len(data_check_buy) == 1:
                        info_order = data_check_buy[0]
                    else:
                        info_order = data_check_buy[-1]

                    print(info_order)

                    if info_order == 'NO DATA ORDER':
                        status_info.config(text='Ждем открытия сделки...', fg='black')
                        if (date_kyiv_not_formated or date_kyiv_not_formated - timedelta(
                                seconds=1) or date_kyiv_not_formated - timedelta(seconds=2)) in dts:
                            print('BYU BTC OR SELL interval 5m')
                            status_info.config(text='Сделка открыта', fg='green')
                            if float(res['k']['c']) > moving_average:
                                await client.create_order(
                                    symbol='BTCUSDT',
                                    side=Client.SIDE_SELL,
                                    type=Client.ORDER_TYPE_MARKET,
                                    quantity=round(btccoin, 6))
                                print('продаем заданный обьем ВТС')
                                data_check_buy.append('Open sell BTC')
                                trades = await client.get_my_trades(symbol='BTCUSDT')
                                order_time = datetime.fromtimestamp(int(trades[-1]['time']) / 1000).strftime(
                                    '%d.%m.%Y %H:%M:%S')
                                order_status = f"{order_time} Пара: {trades[-1]['symbol']}, Цена: {trades[-1]['price']}$, Количество:{trades[-1]['qty']} BTC, {trades[-1]['quoteQty']}$, Продажа BTC\n\n"
                                text1.insert(END, order_status)
                                text1.yview(END)
                            elif float(res['k']['c']) < moving_average:
                                await client.create_order(
                                    symbol='BTCUSDT',
                                    side=Client.SIDE_BUY,
                                    type=Client.ORDER_TYPE_MARKET,
                                    quantity=round(btccoin, 6))
                                print('покупаем заданный объём ВТС')
                                data_check_buy.append('Open buy BTC')
                                trades = await client.get_my_trades(symbol='BTCUSDT')
                                order_time = datetime.fromtimestamp(int(trades[-1]['time']) / 1000).strftime(
                                    '%d.%m.%Y %H:%M:%S')
                                order_status = f"{order_time} Пара: {trades[-1]['symbol']}, Цена: {trades[-1]['price']}$, Количество:{trades[-1]['qty']} BTC, {trades[-1]['quoteQty']}$, Покупка BTC\n\n"
                                text1.insert(END, order_status)
                                text1.yview(END)
                    elif info_order == 'Open sell BTC':
                        print('Пробуєм закупить заданный объём ВТС для закрытия позиции')
                        if float(res['k']['c']) - down_ma <= moving_average <= float(res['k']['c']) + up_ma:  # Close position #інтервал для закриття обраткі
                            await client.create_order(
                                symbol='BTCUSDT',
                                side=Client.SIDE_BUY,
                                type=Client.ORDER_TYPE_MARKET,
                                quantity=round(btccoin, 6))
                            print('Закрыли позицию, ждем новый оредер')
                            data_check_buy.append('NO DATA ORDER')
                            status_info.config(text='Сделка закрыта.(Введите даные для новой сделки)', fg='red')
                            block_all = False
                            e1.config(state=NORMAL)
                            e2.config(state=NORMAL)
                            e3.config(state=NORMAL)
                            button_order.config(state=NORMAL)
                            trades = await client.get_my_trades(symbol='BTCUSDT')
                            order_time = datetime.fromtimestamp(int(trades[-1]['time']) / 1000).strftime('%d.%m.%Y %H:%M:%S')
                            order_status = f"{order_time} Пара: {trades[-1]['symbol']}, Цена: {trades[-1]['price']}$, Количество:{trades[-1]['qty']} BTC, {trades[-1]['quoteQty']}$, 'Покупка BTC'\n\n"
                            text1.insert(END, order_status)
                            text1.yview(END)
                    elif info_order == 'Open buy BTC':
                        print('Пробуєм продать заданный обьем ВТС для закрытия позиции')
                        if float(res['k']['c']) - down_ma <= moving_average <= float(res['k']['c']) + up_ma:  # Close position #інтервал для закриття обраткі
                            await client.create_order(
                                symbol='BTCUSDT',
                                side=Client.SIDE_SELL,
                                type=Client.ORDER_TYPE_MARKET,
                                quantity=round(btccoin, 6))
                            print('Закрыли позицию, ждем новый оредер')
                            data_check_buy.append('NO DATA ORDER')
                            status_info.config(text='Сделка закрыта.(Введите даные для новой сделки)', fg='red')
                            block_all = False
                            e1.config(state=NORMAL)
                            e2.config(state=NORMAL)
                            e3.config(state=NORMAL)
                            button_order.config(state=NORMAL)
                            trades = await client.get_my_trades(symbol='BTCUSDT')
                            order_time = datetime.fromtimestamp(int(trades[-1]['time']) / 1000).strftime(
                                '%d.%m.%Y %H:%M:%S')
                            order_status = f"{order_time} Пара: {trades[-1]['symbol']}, Цена: {trades[-1]['price']}$, Количество:{trades[-1]['qty']} BTC, {trades[-1]['quoteQty']}$, Продажа BTC\n\n"
                            text1.insert(END, order_status)
                            text1.yview(END)


                date_kyiv = datetime.fromtimestamp(int(res['E']) / 1000).strftime('%d.%m.%Y %H:%M:%S')
                klines_nine_ago = await client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_5MINUTE, "50 min ago UTC")
                moving_average = sum(float(klines_nine_ago[i][4]) for i in range(9)) / 9
                balance_btc = await client.get_asset_balance(asset='BTC')
                balance_usdt = await client.get_asset_balance(asset='USDT')
                rate.config(text=res['k']['c'], fg='black')
                kyiv_timezone.config(text=date_kyiv, fg='black')
                ma.config(text=moving_average, fg='black')
                bal_btc.config(text=balance_btc['free'], fg='black')
                bal_usdt.config(text=balance_usdt['free'], fg='black')
                print(date_kyiv)
                print(res['k']['c'])
                print('-------------------------------------------------')





    async def get_btc():
        global block_all
        block_all = True



    root = Tk()
    done = []
    root.geometry('720x585+400+100')
    root.title('BTC/USDT bot trader')
    root.resizable(0, 0)
    asyncio.ensure_future(kline_listener())


    button_order = ttk.Button(text='Создать ордер', command=lambda: asyncio.ensure_future(get_btc()))
    button_order.place(x=25, y=235)

    rate = Label(root, text='btc/usdt', fg='black', font=('Courier New', 16))
    rate.place(x=455, y=20)
    rate_label = Label(root, text='Rate:', fg='black', font=('Courier New', 16))
    rate_label.place(x=400, y=20)

    status_info = Label(root, text='', font=('Comic Sans MS', 18))
    status_info.place(x=25, y=270)


    kyiv_timezone = Label(root, text='time', fg='black', font=('Courier New', 16))
    kyiv_timezone.place(x=455, y=40)
    kyiv_timezone_label = Label(root, text='Kiev/time:', fg='black', font=('Courier New', 16))
    kyiv_timezone_label.place(x=350, y=40)

    ma = Label(root, text='Moving average', fg='black', font=('Courier New', 16))
    ma.place(x=455, y=60)
    ma_label = Label(root, text='MA:', fg='black', font=('Courier New', 16))
    ma_label.place(x=420, y=60)

    bal_btc = Label(root, text='BTC', fg='black', font=('Courier New', 16))
    bal_btc.place(x=455, y=80)
    bal_btc_label = Label(root, text='Balance(BTC):', fg='black', font=('Courier New', 16))
    bal_btc_label.place(x=320, y=80)

    bal_usdt = Label(root, text='USDT', fg='black', font=('Courier New', 16))
    bal_usdt.place(x=455, y=100)
    bal_usdt_label = Label(root, text='Balance(USDT):', fg='black', font=('Courier New', 16))
    bal_usdt_label.place(x=310, y=100)

    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    text1 = Text(root, height=15, width=60, font='Arial 14', wrap=WORD)
    text1.place(x=25, y=310)
    text1.bind("<Key>", lambda a: "break")
    text1.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text1.yview)




    l1 = Label(root, text="Объем ордера(BTC)")
    l1.place(x=25, y=25)
    e1 = Entry(root, width=10)
    e1.place(x=25, y=55)

    l2 = Label(root, text="Отклонение от MA(в BTC) више МА")
    l2.place(x=25, y=95)
    e2 = Entry(root, width=10)
    e2.place(x=25, y=125)

    l3 = Label(root, text="Отклонение от MA(в BTC) ниже МА")
    l3.place(x=25, y=165)
    e3 = Entry(root, width=10)
    e3.place(x=25, y=195)



    while not done:
        root.update()  # process tkinter's events
        await asyncio.sleep(.04)


asyncio.get_event_loop().run_until_complete(main())