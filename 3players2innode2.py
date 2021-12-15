producer1_cap = 100
producer2_cap = 100
producer3_cap = 100
windmill_cap = 70
transmission_cons = 130
producer1_bids = [10,12,14] #node 1
producer2_bids = [11,13] # node 2
producer3_bids = [11.5,12.5] # node 2
producer1_MC = 12 # marginal cost
producer2_MC = 11
producer3_MC = 11.5
producer1_RTMP = producer1_bids[0] # real time market price for producer 1
demand = 230

#initializing lists
NE_for1and2 = []
profits_tables = {}
inc_dec_gaming = []
tso_cost = {}
#make sure bids in the real time market are strategically correct
norwegian_solution = 1 # set the real time price for the player with market power to the prevailing price in the day-ahead market
long_term_contracts = 0 # set the RTMP close to MC, but leaving a slight profit for the players providing flexibility
balance_prices = 0 # set price in the two nodes equal, based on the price in the node without a monopoly, leaving the tso with a cost of 0
taxes = 0
if taxes:
    tax = 0.2
else:
    tax = 1

epsilon = 0.05
if long_term_contracts:
    producer1_bids[0] = producer1_MC*(1-epsilon)
    producer2_bids[-1] = producer2_MC*(1+epsilon)
    producer3_bids[0] = producer3_MC*(1-epsilon)

def calculate_social_welfare(price, tso_cost, producers_profits, key):

    if key in tso_cost.keys():
        tso_cost_here = tso_cost[key]
    else:
        tso_cost_here = 0
    social_welfare = producers_profits[0]+producers_profits[1]+producers_profits[2]-tso_cost_here
    #print(f"The average total social welfare was: {social_welfare}$")
    average_price_total.append(price)
    social_welfares.append(social_welfare)
    tso_costs.append(tso_cost_here)
    prod_profits.append(producers_profits[0]+producers_profits[1]+producers_profits[2])
average_price_total = []
social_welfares = []
average_price = {}
average_price_total = []
prod_profits = []
tso_costs = []

for p3 in range(len(producer3_bids)):
    bimatrix_volume = []
    bimatrix_profit = []
    for x in range(len(producer1_bids)):
        bimatrix_volume.append([])
        bimatrix_profit.append([])
        for _ in range(len(producer2_bids)):
            bimatrix_volume[x].append(_)
            bimatrix_profit[x].append(_)

    for p1 in range(len(producer1_bids)):
        for p2 in range(len(producer2_bids)):
            if producer1_bids[p1]<producer2_bids[p2] and producer2_bids[p2]<producer3_bids[p3]: #lowest bid wins
                p1_volume = producer1_cap
                p2_volume = demand-p1_volume-windmill_cap
                p3_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)
            elif producer1_bids[p1]<producer3_bids[p3] and producer3_bids[p3]<producer2_bids[p2]:
                p1_volume = producer1_cap
                p3_volume = demand-p1_volume-windmill_cap
                p2_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)
            elif producer2_bids[p2]<producer1_bids[p1] and producer1_bids[p1]<producer3_bids[p3]:
                p2_volume = producer2_cap
                p1_volume = demand-p2_volume-windmill_cap
                p3_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)
            elif producer2_bids[p2]<producer3_bids[p3] and producer3_bids[p3]<producer1_bids[p1]:
                p2_volume = producer2_cap
                p3_volume = demand-p2_volume-windmill_cap
                p1_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)
            elif producer3_bids[p3]<producer2_bids[p2] and producer2_bids[p2]<producer1_bids[p1]:
                p3_volume = producer3_cap
                p2_volume = demand-p3_volume-windmill_cap
                p1_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)
            elif producer3_bids[p3]<producer1_bids[p1] and producer1_bids[p1]<producer2_bids[p2]:
                p3_volume = producer3_cap
                p1_volume = demand-p3_volume-windmill_cap
                p2_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)
                
    for p1 in range(len(producer1_bids)):
        for p2 in range(len(producer2_bids)):
            
            #market price in day ahead market, next lowest bid sets price (highest accepted)
            prices = [producer1_bids[p1],producer2_bids[p2],producer3_bids[p3]]
            prices.sort()
            price = prices[1]
            average_price[(p1,p2,p3)]=price
            real_time_market_price = max(float(producer3_MC),producer2_MC) # no one will bid under the highest marginal cost
            if norwegian_solution:
                producer1_RTMP = price
            if long_term_contracts:
                producer1_RTMP = producer1_MC*(1-epsilon)
            if balance_prices:
                producer1_RTMP = real_time_market_price
            #market price for buyers in real time market, when neither p1 nor p3 have a monopoly
            total_redispatch_volume = bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons
            if bimatrix_volume[p1][p2][0]+windmill_cap>transmission_cons: # redispatch for p1, p2, p3
                inc_dec_gaming.append([p1,p2,p3])
                if bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons>-bimatrix_volume[p1][p2][1]+producer2_cap:
                    redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)*tax
                    redispatch_volume_p2 = min(redispatch_volume_p1,producer2_cap - bimatrix_volume[p1][p2][1])
                    redispatch_volume_p3 = redispatch_volume_p1-redispatch_volume_p2
                    producer2_RTMP=real_time_market_price
                    if norwegian_solution:
                        producer3_RTMP = price
                    elif long_term_contracts:
                        producer3_RTMP = producer3_MC*(1+epsilon)
                    else:
                        producer3_RTMP=producer3_bids[-1]
                elif bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons>-bimatrix_volume[p1][p2][2]+producer3_cap:
                    redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)*tax
                    redispatch_volume_p3 = min(redispatch_volume_p1,producer3_cap - bimatrix_volume[p1][p2][2])
                    redispatch_volume_p2 = redispatch_volume_p1-redispatch_volume_p3
                    if norwegian_solution:
                        producer2_RTMP = price
                    elif long_term_contracts:
                        producer2_RTMP = producer2_MC*(1+epsilon)
                    else:
                        producer2_RTMP=producer2_bids[-1]
                    producer3_RTMP=real_time_market_price
                else:
                    if producer2_MC < producer3_MC: #p2 and p3, are both sellers in RTM, lowest MC will bid lowest in real time market
                        redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)*tax
                        redispatch_volume_p2 = min(redispatch_volume_p1,producer2_cap - bimatrix_volume[p1][p2][1])
                        redispatch_volume_p3 = redispatch_volume_p1-redispatch_volume_p2
                        producer2_RTMP=real_time_market_price
                        producer3_RTMP=real_time_market_price
                    else:
                        redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)*tax #redispatch cant be higher than already sold volume
                        redispatch_volume_p3 = min(redispatch_volume_p1,producer3_cap - bimatrix_volume[p1][p2][2])
                        redispatch_volume_p2 = redispatch_volume_p1-redispatch_volume_p3
                        producer3_RTMP=real_time_market_price
                        producer2_RTMP=real_time_market_price

                p1_profit = bimatrix_volume[p1][p2][0]*price-(redispatch_volume_p1*producer1_RTMP+(bimatrix_volume[p1][p2][0]-redispatch_volume_p1)*producer1_MC)
                p2_profit = bimatrix_volume[p1][p2][1]*price + redispatch_volume_p2*producer2_RTMP-(bimatrix_volume[p1][p2][1] + redispatch_volume_p2)*producer2_MC
                p3_profit = bimatrix_volume[p1][p2][2]*price + redispatch_volume_p3*producer3_RTMP-(bimatrix_volume[p1][p2][2] + redispatch_volume_p3)*producer3_MC
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)
                tso_cost[(p1,p2,p3)] = tax*(redispatch_volume_p2*producer2_RTMP+producer3_RTMP*redispatch_volume_p3-total_redispatch_volume*(producer1_RTMP))
            else:
                p1_profit = bimatrix_volume[p1][p2][0]*(price-producer1_MC)
                p2_profit = bimatrix_volume[p1][p2][1]*(price-producer2_MC)
                p3_profit = bimatrix_volume[p1][p2][2]*(price-producer3_MC)
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)

    print("\033[1mPlayer 3 bid is:", producer3_bids[p3],"$\033[")
    print(f"Bimatrix Volume  ┃Player2 bid: {producer2_bids[0]} $    ┃Player2 bid:{producer2_bids[1]}$")
    print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━")
    for i in range(len(bimatrix_volume)):
        print(f"Player1 bid:  {producer1_bids[i]}$┃  {bimatrix_volume[i][0]}       ┃ {bimatrix_volume[i][1]}")
    print("")
    print(f"Bimatrix Profit  ┃Player2 bid: {producer2_bids[0]}$     ┃Player2 bid: {producer2_bids[1]}$")
    print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━")
    for i in range(len(bimatrix_profit)):
        print(f"Player1 bid:  {producer1_bids[i]}$┃",  '{0: <19}'.format(str(bimatrix_profit[i][0])),"┃", '{0: <19}'.format(str(bimatrix_profit[i][1])))
    
    print("")
    profits_tables[p3] = bimatrix_profit

    #finding SPNE
    for p1 in range(len(producer1_bids)):
        leading=[0]
        for p2 in range(len(producer2_bids)):
            if bimatrix_profit[p1][p2][1]>bimatrix_profit[p1][leading[0]][1]:
                leading[0] = p2
            elif bimatrix_profit[p1][p2][1]==bimatrix_profit[p1][leading[0]][1] and leading[0]!=p2:
                leading.append(p2)
        #is leading also optimal for p1?
        for lead in leading:
            flag = True
            for p_1 in range(len(producer1_bids)):
                if bimatrix_profit[p_1][lead][0]>bimatrix_profit[p1][lead][0]:
                    flag = False
            if flag:
                NE_for1and2.append((p1,lead,p3))

def print_tso_cost(tso_cost_key):
    if tso_cost_key in tso_cost:
        print(f"   - The TSO had an extra cost of: {tso_cost[tso_cost_key]}$")

for result in NE_for1and2:
    inc_dec = "[No inc-dec]      "
    if [result[0],result[1],result[2]] in inc_dec_gaming:
            inc_dec = "[Inc-dec apparent]"
    if result[2]==0: # NE_for1and2 given lowest p3 bid, i.e. table 0
        if profits_tables[0][result[0]][result[1]][2]>profits_tables[1][result[0]][result[1]][2]:
            print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[0][result[0]][result[1]])
            print_tso_cost((result[0],result[1],result[2]))
            calculate_social_welfare(average_price[(result[0],result[1],result[2])], tso_cost, profits_tables[0][result[0]][result[1]], (result[0],result[1],result[2]))
    if result[2]==1: # NE_for1and2 given lowest p3 bid, i.e. table 1
        if profits_tables[0][result[0]][result[1]][2]<profits_tables[1][result[0]][result[1]][2]:
            print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[1][result[0]][result[1]])
            print_tso_cost((result[0],result[1],result[2]))        
            calculate_social_welfare(average_price[(result[0],result[1],result[2])], tso_cost, profits_tables[1][result[0]][result[1]], (result[0],result[1],result[2]))
    if profits_tables[0][result[0]][result[1]][2]==profits_tables[1][result[0]][result[1]][2]:
        print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[result[2]][result[0]][result[1]])
        print_tso_cost((result[0],result[1],result[2]))
        calculate_social_welfare(average_price[(result[0],result[1],result[2])], tso_cost, profits_tables[result[2]][result[0]][result[1]], (result[0],result[1],result[2]))
        #print("The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[1] ,"$ for producer 3,"," with profits: ",profits_tables[1][result[0]][result[1]])


print("")
print("These are the averages over all runs and equilibria")
print(f"The total average producers profits was {sum(prod_profits)/len(prod_profits)}")
print(f"The total average tso costs was {sum(tso_costs)/len(tso_costs)}")
print(f"The total average price was {sum(average_price_total)/len(average_price_total)}")
