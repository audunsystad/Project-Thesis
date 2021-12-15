producer1_cap = 100
producer2_cap = 100
producer3_cap = 100
windmill_cap = 70
transmission_cons = 130
producer1_bids = [10,12,14] #node 1
producer2_bids = [11,13] # node 2
producer3_bids = [11.5,12.5] # node 1
producer2_RTMP = producer2_bids[-1] # real time market price for producer 2, as he has locational market power
producer1_MC = 12
producer2_MC = 11
producer3_MC = 11.5
demand = 230

#lists to be used
NE_for1and2 = []
profits_tables = {}
inc_dec_gaming = []
tso_cost = {}

norwegian_solution = 0 # set the real time price for the player with market power to the prevailing price in the day-ahead market
long_term_contracts = 1 # set the RTMP close to MC, but leaving a slight profit for the players providing flexibility
balance_prices = 0 # set price in the two nodes equal, based on the price in the node without a monopoly, leaving the tso with a cost of 0
# - adaptation to the norwegian solution
taxes = 0 #TODO should TSO get income from tax profits? or not? has impliciations on implementation
if taxes: #tax rate is equal to 1-tax (as it is the producers remaining profit)
    tax = 0.5
else:
    tax = 1

if long_term_contracts:
    epsilon = 0.05
    producer1_bids[0] = producer1_MC*(1-epsilon)
    producer2_bids[-1] = producer2_MC*(1+epsilon)
    producer3_bids[0] = producer3_MC*(1-epsilon)

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
            
            #market price in day ahead market
            prices = [producer1_bids[p1],producer2_bids[p2],producer3_bids[p3]]
            prices.sort()
            price = prices[1]
            real_time_market_price = min(float(producer1_MC),producer3_MC) # no one will bid over the lowest marginal cost
            if norwegian_solution:
                producer2_RTMP = price
            if long_term_contracts: 
                producer2_RTMP = max(price,producer2_MC*(1+epsilon))
            if balance_prices:
                producer2_RTMP = real_time_market_price

            #TODO marker hvor det er inc-dec gaming
            #market price for buyers in real time market, when neither p1 nor p3 have a monopoly
            total_redispatch_volume = bimatrix_volume[p1][p2][0]+bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons
            if bimatrix_volume[p1][p2][0]>0 and bimatrix_volume[p1][p2][2]>0: # redispatch for p1, p2, p3
                inc_dec_gaming.append([p1,p2,p3])
                #if producer1_MC < producer3_MC: #highest MC will bid highest in real time market
                if norwegian_solution:
                    if real_time_market_price>price:
                        producer1_RTMP = real_time_market_price
                        producer3_RTMP = real_time_market_price
                    else:
                        producer1_RTMP = price
                        producer3_RTMP = price
                elif long_term_contracts:
                    producer1_RTMP = producer1_MC*(1-epsilon)
                    producer3_RTMP = producer3_MC*(1-epsilon)
                else:
                    if bimatrix_volume[p1][p2][0]>bimatrix_volume[p1][p2][2]: # u1 has monopoly over remaining suply
                        producer1_RTMP = producer1_bids[0]
                        producer3_RTMP = real_time_market_price
                    else:
                        producer3_RTMP = producer3_bids[0]
                        producer1_RTMP = real_time_market_price
                if producer1_RTMP>producer3_RTMP:
                    redispatch_volume_p1 = tax*min(bimatrix_volume[p1][p2][0],bimatrix_volume[p1][p2][0]+bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)
                    redispatch_volume_p2 = tax*(producer2_cap)
                    redispatch_volume_p3 = tax*(bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)
                elif producer1_RTMP<producer3_RTMP:
                    redispatch_volume_p3 = tax*min(bimatrix_volume[p1][p2][2],bimatrix_volume[p1][p2][0]+bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)
                    redispatch_volume_p2 = tax*producer2_cap
                    redispatch_volume_p1 = tax*(bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)
                else:
                    if producer1_MC < producer3_MC: #highest MC will bid highest in real time market
                        redispatch_volume_p3 = tax*min(bimatrix_volume[p1][p2][2],bimatrix_volume[p1][p2][0]+bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)
                        redispatch_volume_p2 = tax*producer2_cap
                        redispatch_volume_p1 = tax*(bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)
                    else:
                        redispatch_volume_p1 = tax*min(bimatrix_volume[p1][p2][0],bimatrix_volume[p1][p2][0]+bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)
                        redispatch_volume_p2 = tax*(producer2_cap)
                        redispatch_volume_p3 = tax*(bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)

                p1_profit = bimatrix_volume[p1][p2][0]*price-(redispatch_volume_p1*producer1_RTMP+(bimatrix_volume[p1][p2][0]-redispatch_volume_p1)*producer1_MC)
                p2_profit = redispatch_volume_p2*producer2_RTMP-redispatch_volume_p2*producer2_MC
                p3_profit = bimatrix_volume[p1][p2][2]*price-(redispatch_volume_p3*producer3_RTMP+(bimatrix_volume[p1][p2][2]-redispatch_volume_p3)*producer1_MC)
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)

                tso_cost[(p1,p2,p3)] = redispatch_volume_p2*producer2_RTMP-redispatch_volume_p3*producer3_RTMP-redispatch_volume_p1*producer1_RTMP
             
            elif windmill_cap+bimatrix_volume[p1][p2][0]>transmission_cons: #redispatch for p1 and p2
                inc_dec_gaming.append([p1,p2,p3])
                redispatch_volume = tax*(bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)
                p1_profit = bimatrix_volume[p1][p2][0]*price-(redispatch_volume*producer1_bids[0]+(bimatrix_volume[p1][p2][0]-redispatch_volume)*producer1_MC)
                p2_profit = bimatrix_volume[p1][p2][1]*price+redispatch_volume*producer2_RTMP-producer2_cap*producer2_MC
                p3_profit = 0
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)
                tso_cost[(p1,p2,p3)] = total_redispatch_volume*(producer2_RTMP-producer1_bids[0])

                
            elif windmill_cap+bimatrix_volume[p1][p2][2]>transmission_cons: #redispatch for p3 and p2
                inc_dec_gaming.append([p1,p2,p3])
                redispatch_volume = tax*(bimatrix_volume[p1][p2][2]+windmill_cap-transmission_cons)
                p1_profit = 0
                p2_profit = bimatrix_volume[p1][p2][1]*price+redispatch_volume*producer2_RTMP-producer2_cap*producer2_MC
                p3_profit = bimatrix_volume[p1][p2][2]*price-(redispatch_volume*producer3_bids[0]+(bimatrix_volume[p1][p2][2]-redispatch_volume)*producer1_MC)              
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)   
                tso_cost[(p1,p2,p3)] = total_redispatch_volume*(producer2_RTMP-producer3_bids[0])
            else:
                p1_profit = bimatrix_volume[p1][p2][0]*(price-producer1_MC)
                p2_profit = bimatrix_volume[p1][p2][1]*(price-producer2_MC)
                p3_profit = bimatrix_volume[p1][p2][2]*(price-producer3_MC)
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)
    print("\033[1mPlayer 3 bid is:", producer3_bids[p3],"$\033[")
    print(f" BBimatrix Volume  ┃Player2 bid: {producer2_bids[0]} $    ┃Player2 bid:{producer2_bids[1]}$")
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
        #print(p1,leading,"here")
        #is leading also optimal for p1?
        for lead in leading:
            flag = True
            for p_1 in range(len(producer1_bids)):
                if bimatrix_profit[p_1][lead][0]>bimatrix_profit[p1][lead][0]:
                    flag = False
            if flag:
                #print("The SPNE bids are: ",producer1_bids[p1], "$ for producer 1, and ",producer2_bids[lead],"$ for producer 2, with profits: ",bimatrix_profit[p1][lead])
                NE_for1and2.append((p1,lead,p3))
    
def print_tso_cost(tso_cost_key):
    if tso_cost_key in tso_cost:
        print(f"   - The TSO had an extra cost of: {tso_cost[tso_cost_key]}$")
        tso_cost_here = tso_cost[tso_cost_key]
    else:
        tso_cost_here = 0
    tso_costs.append(tso_cost_here)

tso_costs = []
prod_profits = []
all_prices = []

for result in NE_for1and2:
    inc_dec = "[No inc-dec]      "
    prices = [producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]]
    prices.sort()
    price = prices[1]
    #append price to all_prices when SPNE is found
    if [result[0],result[1],result[2]] in inc_dec_gaming:
            inc_dec = "[Inc-dec apparent]"
    if result[2]==0: # NE_for1and2 given lowest p3 bid, i.e. table 0
        if profits_tables[0][result[0]][result[1]][2]>profits_tables[1][result[0]][result[1]][2]:
            print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[0][result[0]][result[1]])
            print_tso_cost((result[0],result[1],result[2]))
            prod_profits.append(sum(profits_tables[0][result[0]][result[1]]))
            all_prices.append(price)
            #break
    if result[2]==1: # NE_for1and2 given lowest p3 bid, i.e. table 1
        if profits_tables[0][result[0]][result[1]][2]<profits_tables[1][result[0]][result[1]][2]:
            print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[1][result[0]][result[1]])
            print_tso_cost((result[0],result[1],result[2]))
            prod_profits.append(sum(profits_tables[1][result[0]][result[1]]))
            all_prices.append(price)
            #break
    if profits_tables[0][result[0]][result[1]][2]==profits_tables[1][result[0]][result[1]][2]:
        print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[result[2]][result[0]][result[1]])
        print_tso_cost((result[0],result[1],result[2]))
        prod_profits.append(sum(profits_tables[result[2]][result[0]][result[1]]))
        all_prices.append(price)
        #print("The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[1] ,"$ for producer 3,"," with profits: ",profits_tables[1][result[0]][result[1]])

print("")
print("These are the averages over all runs and equilibria")
print(f"The total average producers profits was {sum(prod_profits)/len(prod_profits)}")
print(f"The total average tso costs was {sum(tso_costs)/len(tso_costs)}")
print(f"The total average price was {sum(all_prices)/len(all_prices)}")

