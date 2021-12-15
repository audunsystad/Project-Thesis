producer1_cap = 100
producer2_cap = 100
producer3_cap = 100
windmill_cap = 70
transmission_cons = 130
producer1_bids = [10,12,14] #node 1
producer2_bids = [11,13] # node 2
producer3_bids = [11.5,12.5] # node 3
producer1_RTMP = producer1_bids[0] # real time market price for producer 2, as he has locational market power
producer1_MC = 12
producer2_MC = 11
producer3_MC = 11.5
demand = 230
import numpy as np

SPNEs = {}

norwegian_solution = 0 # set the real time price for the player with market power to the prevailing price in the day-ahead market
long_term_contracts = 0 # set the RTMP close to MC, but leaving a slight profit for the players providing flexibility
balance_prices = 0 # set price in the two nodes equal, based on the price in the node without a monopoly, leaving the tso with a cost of 0
# - adaptation to the norwegian solution
randomised_bid_selection_old = 0
randomised_bid_selection_new = 1
#find total social welfare


#to find producers cost, compare with non-random and check difference
def print_tso_cost(tso_cost_key):
    if tso_cost_key in tso_cost:
        print(f"   - The TSO had an extra cost of: {tso_cost[tso_cost_key]}$, on average")

def print_cons_cost(cons_cost_key):
    if cons_cost_key in cons_cost:
        print(f"   - The consumers had an extra cost of: {cons_cost[cons_cost_key]}$, on average")

def print_average_price(average_price_key):
    if average_price_key in average_price:
        print(f"   - The average price was: {average_price[average_price_key]}$")
        print("")

def add_to_SPNE_dict(key):
    if key in SPNEs:
        SPNEs[key]+=1
    else:
        SPNEs[key]=1

def return_highest(num1,num2):
    if num1>num2:
        return num1
    else:
        return num2

def add_to_dict(cost_dict, key, value, num_runs):
    if key in cost_dict.keys():
        cost_dict[key] += (demand-windmill_cap)*value/num_runs
    else:
        cost_dict[key] = (demand-windmill_cap)*value/num_runs

def add_to_price_dict(cost_dict, key, value, num_runs):
    if key in cost_dict.keys():
        cost_dict[key] += value/num_runs
    else:
        cost_dict[key] = value/num_runs

def calculate_social_welfare(price, tso_cost, producers_profits, key):

    if key in tso_cost.keys():
        tso_cost_here = tso_cost[key]
    else:
        tso_cost_here = 0
    social_welfare = producers_profits[0]+producers_profits[1]+producers_profits[2]-tso_cost_here#-consumer_cost
    #print(f"The average total social welfare was: {social_welfare}$")
    average_price_total.append(price)
    social_welfares.append(social_welfare)
    tso_costs.append(tso_cost_here)
    prod_profits.append(producers_profits[0]+producers_profits[1]+producers_profits[2])
    

num_runs = 50000
lists_of_all_profits = {}
lists_of_all_profits[0] = []
lists_of_all_profits[1] = []
for x in range(len(producer1_bids)):
    lists_of_all_profits[0].append([])
    lists_of_all_profits[1].append([])
    for i in range(len(producer2_bids)):
        lists_of_all_profits[0][x].append([0.0,0.0,0.0])
        lists_of_all_profits[1][x].append([0.0,0.0,0.0])

tso_cost = {}
cons_cost = {}
average_price = {}
average_price_total = []
social_welfares = []
tso_costs = []
prod_profits = []


for run in range(num_runs):    
    #lists to be used   
    NE_for1and2 = []
    profits_tables = {}
    inc_dec_gaming = []
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
                if randomised_bid_selection_old or randomised_bid_selection_new:
                    rand = np.random.normal(0, 0.5*1.818954026356906) # mean and stdev
                    price_p1,price_p2, price_p3 = producer1_bids[p1],producer2_bids[p2],producer3_bids[p3]
                    diff_p1_p2 = price_p1-price_p2
                    diff_p1_p3 = price_p1-price_p3
                    diff_p2_p3 = price_p2-price_p3
                    
                    if randomised_bid_selection_old:
                        if rand>diff_p1_p2 and rand>diff_p1_p3:
                            p1_volume = producer1_cap
                            if rand>diff_p2_p3:
                                p2_volume = demand-p1_volume-windmill_cap
                                p3_volume = 0
                            else:
                                p3_volume = demand-p1_volume-windmill_cap
                                p2_volume = 0
                        elif rand>diff_p1_p2 and rand<diff_p1_p3:
                            p3_volume = producer3_cap
                            p1_volume = demand-p3_volume-windmill_cap
                            p2_volume = 0
                        elif rand<diff_p1_p2 and rand>diff_p1_p3:
                            p2_volume = producer2_cap
                            p1_volume = demand-p2_volume-windmill_cap
                            p3_volume = 0
                        else:
                            p1_volume = 0
                            if rand>diff_p2_p3:
                                p2_volume = producer2_cap
                                p3_volume = demand-p2_volume-windmill_cap
                            else:
                                p3_volume = producer3_cap
                                p2_volume = demand-p3_volume-windmill_cap
                        #find consumer cost
                    if randomised_bid_selection_new:
                        if price_p1>price_p2 and price_p1>price_p3:
                            p1_volume = 0
                            if rand>diff_p2_p3:
                                p2_volume = producer2_cap
                                p3_volume = demand-p2_volume-windmill_cap
                            else:
                                p3_volume = producer3_cap
                                p2_volume = demand-p3_volume-windmill_cap
                        if price_p2>price_p1 and price_p2>price_p3:
                            p2_volume = 0
                            if rand>diff_p1_p3:
                                p1_volume = producer1_cap
                                p3_volume = demand-p1_volume-windmill_cap
                            else:
                                p3_volume = producer3_cap
                                p1_volume = demand-p3_volume-windmill_cap
                        if price_p3>price_p2 and price_p3>price_p1:
                            p3_volume = 0
                            if rand>diff_p1_p2:
                                p1_volume = producer1_cap
                                p2_volume = demand-p1_volume-windmill_cap
                            else:
                                p2_volume = producer2_cap
                                p1_volume = demand-p2_volume-windmill_cap

                    if price_p1>price_p2 and price_p1>price_p3 and p1_volume!=0:
                        normal_market_price = return_highest(price_p2,price_p3)
                        add_to_dict(cons_cost,(p1,p2,p3),price_p1-normal_market_price, num_runs)
                    if price_p2>price_p1 and price_p2>price_p3 and p2_volume!=0:
                        normal_market_price = return_highest(price_p1,price_p3)
                        add_to_dict(cons_cost,(p1,p2,p3),price_p2-normal_market_price, num_runs)
                    if price_p3>price_p2 and price_p3>price_p1 and p3_volume!=0:
                        normal_market_price = return_highest(price_p2,price_p1)
                        add_to_dict(cons_cost,(p1,p2,p3),price_p3-normal_market_price, num_runs)

                else:
                    if producer1_bids[p1]<producer2_bids[p2] and producer2_bids[p2]<producer3_bids[p3]: #lowest bid wins
                        p1_volume = producer1_cap
                        p2_volume = demand-p1_volume-windmill_cap
                        p3_volume = 0
                    elif producer1_bids[p1]<producer3_bids[p3] and producer3_bids[p3]<producer2_bids[p2]:
                        p1_volume = producer1_cap
                        p3_volume = demand-p1_volume-windmill_cap
                        p2_volume = 0
                    elif producer2_bids[p2]<producer1_bids[p1] and producer1_bids[p1]<producer3_bids[p3]:
                        p2_volume = producer2_cap
                        p1_volume = demand-p2_volume-windmill_cap
                        p3_volume = 0
                    elif producer2_bids[p2]<producer3_bids[p3] and producer3_bids[p3]<producer1_bids[p1]:
                        p2_volume = producer2_cap
                        p3_volume = demand-p2_volume-windmill_cap
                        p1_volume = 0
                    elif producer3_bids[p3]<producer2_bids[p2] and producer2_bids[p2]<producer1_bids[p1]:
                        p3_volume = producer3_cap
                        p2_volume = demand-p3_volume-windmill_cap
                        p1_volume = 0
                    elif producer3_bids[p3]<producer1_bids[p1] and producer1_bids[p1]<producer2_bids[p2]:
                        p3_volume = producer3_cap
                        p1_volume = demand-p3_volume-windmill_cap
                        p2_volume = 0
                bimatrix_volume[p1][p2]=(p1_volume,p2_volume,p3_volume)        
        for p1 in range(len(producer1_bids)):
            for p2 in range(len(producer2_bids)):
                
                #market price in day ahead market, next lowest bid sets price (highest accepted)
                prices = [producer1_bids[p1],producer2_bids[p2],producer3_bids[p3]]
                if randomised_bid_selection_old:
                    volumes = [bimatrix_volume[p1][p2][0],bimatrix_volume[p1][p2][1],bimatrix_volume[p1][p2][2]]
                    if volumes[0]==0:
                        price = return_highest(prices[1],prices[2])
                    elif volumes[1]==0:
                        price = return_highest(prices[0],prices[2])
                    else:
                        price = return_highest(prices[0],prices[1])
                else:
                    prices.sort()
                    price = prices[1]
                real_time_market_price = max(float(producer3_MC),producer2_MC) # no one will bid over the lowest marginal cost
                if norwegian_solution:
                    producer2_RTMP = price
                if long_term_contracts: 
                    producer2_RTMP = producer2_MC*1.05
                if balance_prices:
                    producer2_RTMP = real_time_market_price
                add_to_price_dict(average_price, (p1,p2,p3), price, num_runs)
                #TODO marker hvor det er inc-dec gaming
                #market price for buyers in real time market, when neither p1 nor p3 have a monopoly
                total_redispatch_volume = bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons
                if bimatrix_volume[p1][p2][0]+windmill_cap>transmission_cons: # redispatch for p1, p2, p3
                    inc_dec_gaming.append([p1,p2,p3])
                    if bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons>-bimatrix_volume[p1][p2][1]+producer2_cap:
                        redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)
                        redispatch_volume_p2 = min(redispatch_volume_p1,producer2_cap - bimatrix_volume[p1][p2][1])
                        redispatch_volume_p3 = redispatch_volume_p1-redispatch_volume_p2
                        producer2_RTMP=real_time_market_price
                        producer3_RTMP=producer3_bids[-1]
                    elif bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons>-bimatrix_volume[p1][p2][2]+producer3_cap:
                        redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)
                        redispatch_volume_p3 = min(redispatch_volume_p1,producer3_cap - bimatrix_volume[p1][p2][2])
                        redispatch_volume_p2 = redispatch_volume_p1-redispatch_volume_p3
                        producer2_RTMP=producer2_bids[-1]
                        producer3_RTMP=real_time_market_price
                    else:
                        if producer2_MC < producer3_MC: #p2 and p3, are both sellers in RTM, lowest MC will bid lowest in real time market
                            redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons)
                            redispatch_volume_p2 = min(redispatch_volume_p1,producer2_cap - bimatrix_volume[p1][p2][1])
                            redispatch_volume_p3 = redispatch_volume_p1-redispatch_volume_p2
                            producer2_RTMP=real_time_market_price
                            producer3_RTMP=real_time_market_price
                        else:
                            redispatch_volume_p1 = (bimatrix_volume[p1][p2][0]+windmill_cap-transmission_cons) #redispatch cant be higher than already sold volume
                            redispatch_volume_p3 = min(redispatch_volume_p1,producer3_cap - bimatrix_volume[p1][p2][2])
                            redispatch_volume_p2 = redispatch_volume_p1-redispatch_volume_p3
                            producer3_RTMP=real_time_market_price
                            producer2_RTMP=real_time_market_price

                    p1_profit = bimatrix_volume[p1][p2][0]*price-(redispatch_volume_p1*producer1_RTMP+(bimatrix_volume[p1][p2][0]-redispatch_volume_p1)*producer1_MC)
                    p2_profit = bimatrix_volume[p1][p2][1]*price + redispatch_volume_p2*producer2_RTMP-(bimatrix_volume[p1][p2][1] + redispatch_volume_p2)*producer2_MC
                    p3_profit = bimatrix_volume[p1][p2][2]*price + redispatch_volume_p3*producer3_RTMP-(bimatrix_volume[p1][p2][2] + redispatch_volume_p3)*producer3_MC
                    bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)
                    if (p1,p2,p3) in tso_cost.keys():    
                        tso_cost[(p1,p2,p3)] += (redispatch_volume_p2*producer2_RTMP+producer3_RTMP*redispatch_volume_p3-total_redispatch_volume*(producer1_RTMP))/num_runs
                    else:
                        tso_cost[(p1,p2,p3)] = (redispatch_volume_p2*producer2_RTMP+producer3_RTMP*redispatch_volume_p3-total_redispatch_volume*(producer1_RTMP))/num_runs
                else:
                    p1_profit = bimatrix_volume[p1][p2][0]*(price-producer1_MC)
                    p2_profit = bimatrix_volume[p1][p2][1]*(price-producer2_MC)
                    p3_profit = bimatrix_volume[p1][p2][2]*(price-producer3_MC)
                    bimatrix_profit[p1][p2]=(p1_profit,p2_profit,p3_profit)

        """
        print("\033[1mPlayer 3 bid is:", producer3_bids[p3],"$\033[")
        print(f" Bimatrix Volume  ┃Player2 bid: {producer2_bids[0]} $    ┃Player2 bid:{producer2_bids[1]}$")
        print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━")
        for i in range(len(bimatrix_volume)):
            print(f"Player1 bid:  {producer1_bids[i]}$┃  {bimatrix_volume[i][0]}       ┃ {bimatrix_volume[i][1]}")
        print("")
        print(f" Bimatrix Profit  ┃Player2 bid: {producer2_bids[0]}$     ┃Player2 bid: {producer2_bids[1]}$")
        print("━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━")
        for i in range(len(bimatrix_profit)):
            print(f"Player1 bid:  {producer1_bids[i]}$┃",  '{0: <19}'.format(str(bimatrix_profit[i][0])),"┃", '{0: <19}'.format(str(bimatrix_profit[i][1])))
        
        print("")
        """
        profits_tables[p3] = bimatrix_profit

        if randomised_bid_selection_old or randomised_bid_selection_new:
            for p1 in range(len(producer1_bids)):
                for p2 in range(len(producer2_bids)): #the weighted sum for each scenario
                    lists_of_all_profits[p3][p1][p2][0]+=bimatrix_profit[p1][p2][0]*float(1/num_runs)
                    lists_of_all_profits[p3][p1][p2][1]+=bimatrix_profit[p1][p2][1]*float(1/num_runs)
                    lists_of_all_profits[p3][p1][p2][2]+=bimatrix_profit[p1][p2][2]*float(1/num_runs)

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
    


    for result in NE_for1and2:
        inc_dec = "[No inc-dec]      "
        if [result[0],result[1],result[2]] in inc_dec_gaming:
                inc_dec = "[Inc-dec apparent]"
        if result[2]==0: # NE_for1and2 given lowest p3 bid, i.e. table 0
            if profits_tables[0][result[0]][result[1]][2]>profits_tables[1][result[0]][result[1]][2]:
                #print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[0][result[0]][result[1]])
                #print_tso_cost((result[0],result[1],result[2]))
                add_to_SPNE_dict((producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]))
        if result[2]==1: # NE_for1and2 given lowest p3 bid, i.e. table 1
            if profits_tables[0][result[0]][result[1]][2]<profits_tables[1][result[0]][result[1]][2]:
                #print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[1][result[0]][result[1]])
                #print_tso_cost((result[0],result[1],result[2]))
                add_to_SPNE_dict((producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]))

        if profits_tables[0][result[0]][result[1]][2]==profits_tables[1][result[0]][result[1]][2]:
            #print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",profits_tables[result[2]][result[0]][result[1]])
            #print_tso_cost((result[0],result[1],result[2]))
            add_to_SPNE_dict((producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]))





for line in lists_of_all_profits[0]:
    print(line)
for line in lists_of_all_profits[1]:
    print(line)

print("")
#finding SPNE
NE_for1and2 = []
for p3 in lists_of_all_profits:
    bimatrix_profit = lists_of_all_profits[p3]
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

for matrix_key in lists_of_all_profits:
    bimatrix_profit=lists_of_all_profits[matrix_key]
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
for result in NE_for1and2:
    inc_dec = "[No inc-dec]      "
    if producer1_bids[result[0]]<producer2_bids[result[1]] and producer1_bids[result[0]]<producer3_bids[result[2]]:
            inc_dec = "[Inc-dec apparent]"
    if result[2]==0: # NE_for1and2 given lowest p3 bid, i.e. table 0
        if lists_of_all_profits[0][result[0]][result[1]][2]>lists_of_all_profits[1][result[0]][result[1]][2]:
            print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",lists_of_all_profits[0][result[0]][result[1]])
            print_tso_cost((result[0],result[1],result[2]))
            print_cons_cost((result[0],result[1],result[2]))
            print_average_price((result[0],result[1],result[2]))
            calculate_social_welfare(average_price[(result[0],result[1],result[2])], tso_cost, lists_of_all_profits[0][result[0]][result[1]], (result[0],result[1],result[2]))
            add_to_SPNE_dict((producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]))
            #break
    if result[2]==1: # NE_for1and2 given lowest p3 bid, i.e. table 1
        if lists_of_all_profits[0][result[0]][result[1]][2]<lists_of_all_profits[1][result[0]][result[1]][2]:
            print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",lists_of_all_profits[1][result[0]][result[1]])
            print_tso_cost((result[0],result[1],result[2]))
            print_cons_cost((result[0],result[1],result[2]))
            print_average_price((result[0],result[1],result[2]))
            calculate_social_welfare(average_price[(result[0],result[1],result[2])], tso_cost, lists_of_all_profits[1][result[0]][result[1]], (result[0],result[1],result[2]))

            add_to_SPNE_dict((producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]))
            #break

    if lists_of_all_profits[0][result[0]][result[1]][2]==lists_of_all_profits[1][result[0]][result[1]][2]:
        print(f"{inc_dec} The SPNE bids are: ",producer1_bids[result[0]], "$ for producer 1, and ",producer2_bids[result[1]],"$ for producer 2,",producer3_bids[result[2]] ,"$ for producer 3,"," with profits: ",lists_of_all_profits[result[2]][result[0]][result[1]])
        print_tso_cost((result[0],result[1],result[2]))
        print_cons_cost((result[0],result[1],result[2]))
        print_average_price((result[0],result[1],result[2]))
        calculate_social_welfare(average_price[(result[0],result[1],result[2])], tso_cost, lists_of_all_profits[result[2]][result[0]][result[1]], (result[0],result[1],result[2]))
        add_to_SPNE_dict((producer1_bids[result[0]],producer2_bids[result[1]],producer3_bids[result[2]]))

#print(f"The total average social welfare was {sum(social_welfares)/len(social_welfares)}")
print(f"The total average producers profits was {sum(prod_profits)/len(prod_profits)}")
print(f"The total average tso costs was {sum(tso_costs)/len(tso_costs)}")
print(f"The total average price was {sum(average_price_total)/len(average_price_total)}")