from easyT.manager import Manager
from easyT.platforms import Platforms
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# Teste Joao Euko easyT

symbol = 'GBPUSD'
platform = Platforms().METATRADER5

manager = Manager()

manager.set_platform(platform)
initialize = manager.get_initialize()

initialize.initialize_platform()
initialize.initialize_symbol(symbol)

rates = manager.get_rates(2, symbol, 15)
rates_close = rates.close

# Configuracao parametros da biblioteca Pandas

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

# Coletando as linhas pro canal

linhas = pd.read_csv("Tabelacanais750.csv")

# Criando o ativo a ser operado

ativo = 'GBPUSD'

# Iniciando o MT5

mt5.initialize()
selecionado = mt5.symbol_select(ativo)

# Configurando horario de negociacao

horario_inicio = pd.Timestamp(datetime.today().strftime(('%Y-%m-%d') + '-00:00:00'))
horario_fechamento = pd.Timestamp(datetime.today().strftime(('%Y-%m-%d') + '-23:45:00'))

preco_ask = mt5.symbol_info_tick(ativo).ask
preco_bid = mt5.symbol_info_tick(ativo).bid


# Funcao de Venda

def venda(ativo, quantidade, sl, tp):
    print('Venda efetuada')
    lot = float(quantidade)
    symbol = ativo
    price = mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point
    deviation = 0

    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': lot,
        'type': mt5.ORDER_TYPE_SELL,
        'price': price,
        'sl': sl,
        'tp': tp,
        'deviation': deviation,
        'magic': 11031994,
        'comment': 'Ordem de venda enviada',
        'type_time': mt5.ORDER_TIME_DAY,
        'type_filling': mt5.ORDER_FILLING_FOK
    }

    resultado = mt5.order_send(request)
    return resultado


# Funcao de compra
def compra(ativo, quantidade, sl, tp):
    print('Compra efetuada')
    lot = float(quantidade)
    symbol = ativo
    price = mt5.symbol_info_tick(symbol).ask
    point = mt5.symbol_info(symbol).point
    deviation = 0

    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': lot,
        'type': mt5.ORDER_TYPE_BUY,
        'price': price,
        'sl': sl,
        'tp': tp,
        'deviation': deviation,
        'magic': 11031994,
        'comment': 'Ordem de compra enviada',
        'type_time': mt5.ORDER_TIME_DAY,
        'type_filling': mt5.ORDER_FILLING_FOK
    }

    resultado = mt5.order_send(request)
    return resultado


# Funcao de fechamento de ordens abertas
def fechamento_de_posicoes(position):
    print('Acabou o Tempo')
    tick = mt5.symbol_info_tick(position.symbol)
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'position': position.ticket,
        'symbol': position.volume,
        'type': mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
        'price': tick.ask if position.type == 1 else tick.bid,
        'deviation': 20,
        'magic': 30031994,
        'comment': 'fechamento da ordem, acabou o tempo',
        'type_time': mt5.ORDER_TIME_DAY,
        'type_filling': mt5.ORDER_FILLING_FOK
    }
    resultado = mt5.order_send(request)
    return resultado


# Criando lista de canal principal e canal secundario.
lista_canais = []


positions = mt5.positions_get()
print(positions)


while True:

    preco_ask = round(mt5.symbol_info_tick(ativo).ask, 5)
    #preco_ask = float(input('Preco do mercado: '))

    if round(preco_ask, 5) != round(mt5.symbol_info_tick(ativo).ask, 5):
        rates = manager.get_rates(2, symbol, 15)
        rates_close = rates.close
        local_preco = linhas.loc[linhas.values == round(preco_ask, 5)]
        canal_preco = local_preco['Canal'].item()
        local_close = linhas.loc[linhas.values == round(rates_close[0], 5)]
        canal_close = round(local_close['Canal'].item(), 5)
        #canal_close = float(input('Em Qual canal fechou? '))
        hora_agora = datetime.now()
        to_dentro_horario = horario_inicio <= hora_agora <= horario_fechamento
        total_ordens_abertas = mt5.orders_total()
        total_posicoes_abertas = mt5.positions_total()
        posicoes_abertas = mt5.positions_get()

        if total_ordens_abertas > 0 or total_posicoes_abertas > 0:
            if hora_agora > horario_fechamento:
                for posicoes in positions:
                    fechamento_de_posicoes(posicoes)

        if canal_preco in lista_canais:
            #print('Esta no mesmo Canal')
            if canal_preco != lista_canais[1]:
                lista_canais.append(canal_preco)
                lista_canais.pop(0)
        else:
            #print('\033[43m MUDANCA DE CANAL \033[m')
            if len(lista_canais) <= 1:
                lista_canais.append(canal_preco)
                print(f'Esta no canal {canal_preco}')
                print(f'\033[43m FOI ADICIONADO O CANAL {canal_preco} A LISTA \033[m')
                print(lista_canais)

            if len(lista_canais) >= 2:
                # Canal atual MAIOR que o canal de referencia(CR) e zona neutra(ZN)
                if lista_canais[0] < canal_preco > lista_canais[1]:
                    if total_ordens_abertas > 0 or total_posicoes_abertas > 0:
                        if preco_ask > local_preco["120"].item():
                            lista_canais.pop(0)
                            lista_canais.append(canal_preco)
                            #print(lista_canais)
                            #print('\033[43mHouve uma troca na lista.\033[m')

                    if (canal_preco - 1) == lista_canais[1]:
                        #print('\033[32m POSSIVEL COMPRA \033[m')
                        sl_canal = (local_preco - 2)['Canal'].item()
                        sl = linhas.loc[linhas.values == sl_canal]
                        sl = round(sl['140'].item(), 5)
                        tp_canal = (local_preco + 1)['Canal'].item()
                        tp = linhas.loc[linhas.values == tp_canal]
                        tp = round(tp['149'].item(), 5)
                        # Nenhuma ordem aberta
                        if total_ordens_abertas == 0 and total_posicoes_abertas == 0:

                            if preco_ask < local_preco["120"].item():

                                if lista_canais[0] < canal_close > lista_canais[1]:
                                    compra(ativo, 1, sl, tp)
                                    lista_canais.pop(0)
                                    lista_canais.append(canal_preco)

                            if preco_ask > local_preco["120"].item():
                                lista_canais.pop(0)
                                lista_canais.append(canal_preco)
                                #print(lista_canais)
                                #print('\033[43mHouve uma troca na lista.\033[m')



                # Canal atual MENOR que o canal de referencia(CR) e zona neutra(ZN)
                if lista_canais[0] > canal_preco < lista_canais[1]:
                    if total_ordens_abertas > 0 or total_posicoes_abertas > 0:
                        if preco_ask < local_preco["40"].item():
                            lista_canais.pop(0)
                            lista_canais.append(canal_preco)
                            #print(lista_canais)
                            #print('\033[43mHouve uma troca na lista.\033[m')

                    else:
                        if (canal_preco + 1) == lista_canais[1]:
                            print('\033[31m POSSIVEL VENDA \033[m')
                            sl_canal = (local_preco + 2)['Canal'].item()
                            sl = linhas.loc[linhas.values == sl_canal]
                            sl = round(sl['21'].item(), 5)
                            tp_canal = (local_preco - 1)['Canal'].item()
                            tp = linhas.loc[linhas.values == tp_canal]
                            tp = round(tp['15'].item(), 5)

                            # Nenhuma ordem aberta
                            if total_ordens_abertas == 0 and total_posicoes_abertas == 0:

                                if preco_ask > local_preco["40"].item():

                                    if lista_canais[0] > canal_close < lista_canais[1]:
                                        venda(ativo, 1, sl, tp)
                                        lista_canais.pop(0)
                                        lista_canais.append(canal_preco)

                                if preco_ask < local_preco["40"].item():
                                    lista_canais.pop(0)
                                    lista_canais.append(canal_preco)
                                    #print(lista_canais)
                                    #print('\033[43mHouve uma troca na lista.\033[m')


        '''print(f'Valor do mercado: {preco_ask}')
        print(f'Horario: {hora_agora}')
        print(f'Ordens Abertas: {total_ordens_abertas}')
        print(f'Posicoes Abertas: {total_posicoes_abertas}')
        print(f'Esta no Canal -> \033[1;34m{canal_preco}\033[m')
        print(f'Lista de Canais -> {lista_canais}')
        print(f'Ultimo Fechamento de vela -> {round(rates_close[0],5)} no Canal -> {canal_close}')
        print('-' * 40)'''