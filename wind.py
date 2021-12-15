producer1_cap = 100
producer2_cap = 100
windmill_caps = [50,70] #has to be between 30 and 130, and with two possible outcomes, in order for maxmin to work properly
windmill_prob = [0.5,0.5] # has to be same length as windmill_caps
transmission_cons = 130
producer1_bids = [10,12,14]
producer2_bids = [11,13]
producer1_RTMP = producer1_bids[0]
producer2_RTMP = producer2_bids[-1]
producer1_MC = 12
producer2_MC = 11
demand = 230
profit_tables = {}
inc_dec_gaming = []
tso_cost = {}

norwegian_solution = 0 # set the real time price for the player with market power to the prevailing price in the day-ahead market
    # - is implementation above market based? should only be set if there is inc-dec, not if there is redispatch
long_term_contracts = 0 # set the RTMP close to MC, but leaving a slight profit for the players providing flexibility
balance_prices = 0 # set price in the two nodes equal, leaving the tso with a cost of 0
randomised_bid_selection = 0
taxes = 0 #"tax" that falls to the TSO
if taxes:
    tax = 0.5
else:
    tax = 1

if long_term_contracts:
    epsilon = 0.1
    producer2_bids[-1] = producer2_MC*(1+epsilon)
    producer1_bids[0] = producer2_MC*(1-epsilon)

#First we initialize the matrices to be used
for windmill_cap in windmill_caps:
    bimatrix_volume = []
    bimatrix_profit = []
    profit_tables["expected value"] = []
    profit_tables["minmax"] = []
    for x in range(len(producer1_bids)):
        bimatrix_volume.append([])
        bimatrix_profit.append([])
        profit_tables["expected value"].append([])
        profit_tables["minmax"].append([])
        for _ in range(len(producer2_bids)):
            bimatrix_volume[x].append(_)
            bimatrix_profit[x].append(_)
            profit_tables["expected value"][x].append([0,0])
            profit_tables["minmax"][x].append([0,0])

    #here we determine what volumes each producer gets to sell, lowest bid wins
    for p1 in range(len(producer1_bids)):
        for p2 in range(len(producer2_bids)):
            if producer1_bids[p1]<producer2_bids[p2]: #lowest bid wins
                bimatrix_volume[p1][p2]=(producer1_cap,demand-producer1_cap-windmill_cap)
            elif producer1_bids[p1]==producer2_bids[p2]: #equal bids yield shared volume
                bimatrix_volume[p1][p2]=((demand-windmill_cap)/2,(demand-windmill_cap)/2)
            else:
                bimatrix_volume[p1][p2]=(demand-producer2_cap-windmill_cap,producer2_cap)

    #here we determine the profits each producer achieves, given the wind and bids
    for p1 in range(len(producer1_bids)):
        for p2 in range(len(producer2_bids)):
            price = max(producer1_bids[p1],producer2_bids[p2])
            if norwegian_solution: 
                producer1_RTMP = price
                producer2_RTMP = price
            if long_term_contracts:
                producer1_RTMP = producer1_MC*(1-epsilon)
                producer2_RTMP = producer2_MC*(1+epsilon)
            if windmill_cap+bimatrix_volume[p1][p2][0]>transmission_cons: #these are the profits given redispatch
                inc_dec_gaming.append([p1,p2]) # marking where we have redispatch 
                redispatch_volume = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)*tax
                p1_profit = bimatrix_volume[p1][p2][0]*price-(redispatch_volume*producer1_RTMP+(bimatrix_volume[p1][p2][0]-redispatch_volume)*producer1_MC)
                p2_profit = bimatrix_volume[p1][p2][1]*price+redispatch_volume*producer2_RTMP-producer2_cap*producer2_MC
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit) #the extra cost that the tso has to cover
                tso_cost[(p1,p2)]=redispatch_volume*(producer2_bids[-1]-producer1_bids[0])
            else: #these are the profits when redispatch does not happen
                p1_profit = bimatrix_volume[p1][p2][0]*(price-producer1_MC)
                p2_profit = bimatrix_volume[p1][p2][1]*(price-producer2_MC)
                bimatrix_profit[p1][p2]=(p1_profit,p2_profit)

    #here we are printing the bimatrix volume and profits
    print("\033[1mWindmill cap is:", windmill_cap,"\033[")
    print(f"BBimatrix Volume  ┃Player2 bid: {producer2_bids[0]} $ ┃Player2 bid:{producer2_bids[1]}$")
    print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━")
    for i in range(len(bimatrix_volume)):
        print(f"Player1 bid:  {producer1_bids[i]}$┃  {bimatrix_volume[i][0]}       ┃ {bimatrix_volume[i][1]}")
    print("")
    print(f"Bimatrix Profit  ┃Player2 bid: {producer2_bids[0]}$  ┃Player2 bid: {producer2_bids[1]}$")
    print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━")
    for i in range(len(bimatrix_profit)):
        print(f"Player1 bid:  {producer1_bids[i]}$┃",  '{0: <16}'.format(str(bimatrix_profit[i][0])),"┃", '{0: <16}'.format(str(bimatrix_profit[i][1])))
    
    print("")
    profit_tables[windmill_cap] = bimatrix_profit

#creating maxmin table 
for p1 in range(len(producer1_bids)):
    for p2 in range(len(producer2_bids)):
        if profit_tables[windmill_caps[0]][p1][p2][0]<=profit_tables[windmill_caps[1]][p1][p2][0]:
            profit_tables["minmax"][p1][p2][0]+=profit_tables[windmill_caps[0]][p1][p2][0]
        else:
            profit_tables["minmax"][p1][p2][0]+=profit_tables[windmill_caps[1]][p1][p2][0]
        if profit_tables[windmill_caps[0]][p1][p2][1]<=profit_tables[windmill_caps[1]][p1][p2][1]:
            profit_tables["minmax"][p1][p2][1]+=profit_tables[windmill_caps[0]][p1][p2][1]
        else:
            profit_tables["minmax"][p1][p2][1]+=profit_tables[windmill_caps[1]][p1][p2][1]

#finding SPNE with maxmin (optimal choice is what gives the best outcome in worst case scenario (lowest loss))
bimatrix_profit = profit_tables["minmax"]
print("\033[1mMaxMin matrix\033[")
print("")
print(f" BBimatrix Profit  ┃Player2 bid: {producer2_bids[0]}$  ┃Player2 bid: {producer2_bids[1]}$")
print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━")
for i in range(len(bimatrix_profit)):
    print(f"Player1 bid:  {producer1_bids[i]}$┃",  '{0: <16}'.format(str(bimatrix_profit[i][0])),"┃", '{0: <16}'.format(str(bimatrix_profit[i][1])))

print("")
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
        
        inc_dec = "[No inc-dec]      "
        if [p1,p2] in inc_dec_gaming:
            inc_dec = "[Inc-dec apparent]"

        if flag:
            print(f"{inc_dec} The maxmin-SPNE bids are: ",producer1_bids[p1], "$ for producer 1, and ",producer2_bids[lead],"$ for producer 2, with profits: ",bimatrix_profit[p1][lead])
            if (p1,lead) in tso_cost:
                print(f"   - The TSO had an extra cost of: {tso_cost[(p1,lead)]}$")

#finding expected value of profit 
for i in range(len(windmill_caps)):
    for p1 in range(len(producer1_bids)):
        for p2 in range(len(producer2_bids)): #the weighted sum for each scenario
            profit_tables["expected value"][p1][p2][0]+=profit_tables[windmill_caps[i]][p1][p2][0]*windmill_prob[i]
            profit_tables["expected value"][p1][p2][1]+=profit_tables[windmill_caps[i]][p1][p2][1]*windmill_prob[i]

#finding SPNE with expected value
bimatrix_profit = profit_tables["expected value"]
print("\033[1mExpected value matrix\033[")
print("")
print(f" BBimatrix Profit  ┃Player2 bid: {producer2_bids[0]}$  ┃Player2 bid: {producer2_bids[1]}$")
print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━")
for i in range(len(bimatrix_profit)):
    print(f"Player1 bid:  {producer1_bids[i]}$┃",  '{0: <16}'.format(str(bimatrix_profit[i][0])),"┃", '{0: <16}'.format(str(bimatrix_profit[i][1])))

print("")
sum_of_profits = []
sum_of_tso_cost = []
sum_of_prices = []
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
        inc_dec = "[No inc-dec]      "
        if [p1,p2] in inc_dec_gaming:
            inc_dec = "[Inc-dec apparent]"

        if flag:
            print(f"{inc_dec} The expected value-SPNE bids are: ",producer1_bids[p1], "$ for producer 1, and ",producer2_bids[lead],"$ for producer 2, with profits: ",bimatrix_profit[p1][lead])
            sum_of_profits.append(sum(bimatrix_profit[p1][lead]))
            sum_of_prices.append(max(producer1_bids[p1], producer2_bids[lead]))
            if (p1,lead) in tso_cost:
                print(f"   - The TSO had an extra cost of: {tso_cost[(p1,lead)]}$")
                sum_of_tso_cost.append(tso_cost[(p1,lead)])
            else:
                sum_of_tso_cost.append(0)

print("")
print("These are the averages over all runs and equlibria")
print(f"the average profits for producers were {sum(sum_of_profits)/len(sum_of_profits)}")
print(f"the average of tso_costs were {sum(sum_of_tso_cost)/len(sum_of_tso_cost)}")
print(f"the average of price were {sum(sum_of_prices)/len(sum_of_prices)}")
