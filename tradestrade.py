#coding=utf-8

from kuanke.user_space_api import *

class trade_stat():
    def __init__(self):
        self.trade_total_count = 0
        self.trade_success_count = 0
        self.earn_money = 0
        self.lost_money = 0
        self.statis = {'win': [], 'loss': []}
        
    def reset(self):
        self.trade_total_count = 0
        self.trade_success_count = 0
        self.earn_money = 0
        self.lost_money = 0
        self.statis = {'win': [], 'loss': []}
    
    # 记录交易次数便于统计胜率
    # 卖出成功后针对卖出的量进行盈亏统计
    def watch(self, stock, sold_amount, avg_cost, cur_price):
        self.trade_total_count += 1
        current_value = sold_amount * cur_price
        cost = sold_amount * avg_cost

        percent = round((current_value - cost) / cost * 100, 2)
        if current_value > cost:
            self.earn_money += current_value - cost
            self.trade_success_count += 1
            win = [stock, percent]
            self.statis['win'].append(win)
        else:
            self.lost_money += cost - current_value
            loss = [stock, percent]
            self.statis['loss'].append(loss)
        
    def report(self, context):
        cash = context.portfolio.cash
        totol_value = context.portfolio.portfolio_value
        position = 1 - cash/totol_value
        log.info("收盘后持仓概况:%s" % str(list(context.portfolio.positions)))
        log.info("仓位概况:%.2f" % position)
        self.print_win_rate(context.current_dt.strftime("%Y-%m-%d"), context.current_dt.strftime("%Y-%m-%d"), context)
        self.print_win_lost(context.current_dt.strftime("%Y-%m-%d"), context.current_dt.strftime("%Y-%m-%d"), context)
    
    # 打印均赢额，均亏额，盈亏比
    def print_win_lost(self, current_date, print_date, context):
        if str(current_date) == str(print_date):
            jye = 0
            jke = 0
            ykb = 0
            if 0 < self.trade_total_count and 0 < self.trade_success_count:
                jye = round(self.earn_money/float(self.trade_total_count),3)
                jke = round(self.lost_money/float(self.trade_total_count),3)
                if jke > 0:
                    ykb = round(jye/jke,3)
            print "-"
            print '------------盈亏比报表------------'
            print '均赢额:{0}, 均亏额{1}, 盈亏比{2}'.format(jye, jke, str(ykb * 100) + str('%'))
            print '--------------------------------'
            print "-"
            
            
    # 打印胜率
    def print_win_rate(self, current_date, print_date, context):
        if str(current_date) == str(print_date):
            win_rate = 0
            if 0 < self.trade_total_count and 0 < self.trade_success_count:
                win_rate = round(self.trade_success_count / float(self.trade_total_count), 3)

            most_win = self.statis_most_win_percent()
            most_loss = self.statis_most_loss_percent()
            starting_cash = context.portfolio.starting_cash
            total_profit = self.statis_total_profit(context)
            if len(most_win)==0 or len(most_loss)==0:
                return

            print "-"
            print '------------绩效报表------------'
            print '交易次数: {0}, 盈利次数: {1}, 胜率: {2}'.format(self.trade_total_count, self.trade_success_count, str(win_rate * 100) + str('%'))
            print '单次盈利最高: {0}, 盈利比例: {1}%'.format(most_win['stock'], most_win['value'])
            print '单次亏损最高: {0}, 亏损比例: {1}%'.format(most_loss['stock'], most_loss['value'])
            print '总资产: {0}, 本金: {1}, 盈利: {2}, 盈亏比率：{3}%'.format(starting_cash + total_profit, starting_cash, total_profit, total_profit / starting_cash * 100)
            print '--------------------------------'
            print "-"

    # 统计单次盈利最高的股票
    def statis_most_win_percent(self):
        result = {}
        for statis in self.statis['win']:
            if {} == result:
                result['stock'] = statis[0]
                result['value'] = statis[1]
            else:
                if statis[1] > result['value']:
                    result['stock'] = statis[0]
                    result['value'] = statis[1]

        return result

    # 统计单次亏损最高的股票
    def statis_most_loss_percent(self):
        result = {}
        for statis in self.statis['loss']:
            if {} == result:
                result['stock'] = statis[0]
                result['value'] = statis[1]
            else:
                if statis[1] < result['value']:
                    result['stock'] = statis[0]
                    result['value'] = statis[1]

        return result

    # 统计总盈利金额    
    def statis_total_profit(self, context):
        return context.portfolio.portfolio_value - context.portfolio.starting_cash