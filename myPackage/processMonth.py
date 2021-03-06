# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:31:41 2021

@author: anddy
"""

import numpy as np
from matplotlib import pyplot as plt
import processCorr as pCor
import processReadData as pRd
import os
import time
import warnings
import std_risetime as srt
mon = pRd.read_data()

def wakeupStreak():
    all_dat = pRd.read_All()[0]
    rise_streak = []
    risetime = all_dat['Rise time']
    risetime.reverse()
    for day in risetime:
        if day > 120:
            break
        else:
            rise_streak.append(day)
    total_streak = []
    totals = list(np.array(all_dat['Total'])*100)
    totals.reverse()
    for day in totals:
        if day < 70:
            break
        else:
            total_streak.append(day)
    
    return len(rise_streak), len(total_streak)


def monthly_eval(mon):
    if len(mon['Name']) > 31:
        dat = 'semester'
    else:
        dat = 'monthly'
    warnings.filterwarnings('ignore')
    # rt: plot 2 (histogram)
    #rt = list(mon['Rise time'])
    changed_occurence = srt.changed_risetime()
    rt = srt.rise_time_adjustment(mon, changed_occurence)

    # rt2: plot 1
    rt2 = np.array(srt.rise_time_adjustment(mon, changed_occurence))    # Divide in order for it to fin into the graph
    divgraph = 3
    rt2 = list(rt2/divgraph)
    fig, axe = plt.subplots(2,1, figsize = (12,9), gridspec_kw={'height_ratios': [2, 1]})
    fig.tight_layout(h_pad = 6)
    
    # Set up time range
    if min(rt) > 0:
        start_p = 0
    elif min(rt) < 1:
        start_p = min(rt)      
    if max(rt) > 240:
        end_p = max(rt)
    elif max(rt) < 241:
        end_p = 240
    
    rt_bin = np.linspace(start_p,end_p, 8)
    
    beg_time = 32400 + start_p*60
    end_time = 32400 + end_p*60
    interval = (end_time-beg_time)/ 6
    interval = interval - (interval%300)
    
    # Set Time values for the Histogram
    Rtime = []
    hour = beg_time        # Add or subtract 3600 to adjust
    for i in range(8):
        Rtime.append(str(time.strftime('%H:%M',time.gmtime(hour))))
        hour += interval
    
    # figure out each values in rise time hist == t_vals
    c = []
    t_vals = []
    cc = 1
    
    for i in rt_bin:
        for j in rt:
            try:
                if float(i) <= float(j) <= float(rt_bin[cc]):
                    c.append(j)
            except:
                pass
        cc+=1
        t_vals.append(len(c))
        c = []

    # write in the values
    for j in range(len(rt_bin)):
        if t_vals[j] == 0:
            pass
        else:
            axe[1].text(rt_bin[j]+11, t_vals[j]+.5, t_vals[j], color = 'r')
    
    # Set up date for xticklabels
    date = []
    if '/' in mon['Name'][0] and '/' in mon['Name'][-1]:
        for d in mon['Name']:
            d = d.split('/')
            date.append(d[1][:2].strip(' '))
    else:
        for d in mon['Date']:
            if 'semester' in dat:
                '''
                IN PROGRESS
                '''
            elif '-' in d:
                d = d.split('-')
                date.append(d[2][:2])
            else:
                d = d.split('/')
                date.append(d[1][:2].strip(' '))
    # Plot Histogram
    axe[1].hist(rt, rt_bin, color = 'orange', width = 26)
    axe[1].set_ylim((0,max(t_vals)+3))
    axe[1].set_title('Rise Time Histogram', fontsize = 15, fontweight = 'bold')
    axe[1].set_xlabel('Time', fontsize = 13)
    axe[1].set_ylabel('occurence', fontsize = 13)
    axe[1].set_xticks(np.linspace(start_p,end_p,8))
    axe[1].set_xticklabels(Rtime)
    
    # Add Average wake up time
    avgRT = np.sum(rt)/len(rt)
    avgRT_time = str(time.strftime('%H:%M',time.gmtime(avgRT*60+32400)))
    axe[1].text(avgRT, max(t_vals)+2,'*avg RT: '+avgRT_time+'*',color='red',alpha=.8)
    for i in range(max(t_vals)+2):
        axe[1].text(avgRT, i,'|',color='red',alpha=.8)
    
    # Plot Rise time 
    # set y limits
    ylimits = np.linspace(start_p,end_p,6)
    ylim = []
    for i in ylimits:
        ylim.append(time.strftime('%H:%M',time.gmtime(i*60 + 32400)))
    axe0 = axe[0].twinx()
    axe0.plot(rt2,'g-.', label = 'Rise time (m)+', alpha=.3)
    axe0.set_ylim((min(rt2),max(rt2)+20))
    axe0.set_ylabel('Rise Time', fontsize = 13,color = 'g',alpha=.8)
    axe0.yaxis.set_label_position("right")
    axe0.set_yticks(ylimits/divgraph)
    axe0.set_yticklabels(ylim)
    
    # Meditation
    m = list(mon['Meditation'])
    x_positions = np.arange(0,len(m))
    axe[0].bar(x_positions,m, color ='orange', label = 'Meditation (min)', alpha = .5)
    
    # Personal Reading
    pr = np.array(mon['Reading'])
    x_positions = np.arange(0,len(pr))
    axe[0].bar(x_positions,pr, color = 'red', label = 'Reading (min)', alpha = .5)
    
    
    # total
    tt = np.array(list(mon['Total']))
    if 'semester' in dat:
        date_x = np.arange(0,4)
    else:
        date_x = np.arange(0,len(tt))
    
    axe[0].plot(tt*100, 'm', lw=2, alpha = .3, label = 'Total (%)')
    axe[0].set_title('Total %', fontsize = 15, fontweight = 'bold')
    axe[0].set_xlabel('Date', fontsize = 13)
    axe[0].set_ylabel('Productivity', fontsize= 13,color='m',alpha=.8)
    axe[0].set_xticks(date_x)
    axe[0].set_xticklabels(date)
    axe[0].set_ylim((0,np.max(tt*100)+30))
    axe[0].plot(0,-1,'r.',label = 'Drink') 
    axe[0].plot(0,-1,'w.',lw=2)        
    axe[0].plot(0,0,'g-.', label = 'Rise time', alpha=.3)
    axe[0].legend()
    
    # Days I drank
    dk = np.array(list(mon['Drink']))
    for i in range(len(dk)):
        if dk[i] > 0:
            axe[0].plot(date_x[i],tt[i]*100,'r.',lw=3)        

    # Personal Reading - Books Finished
    try:
        bf = mon['Books finished']
        for i in range(len(bf)):
            if bf[i] == 1.0 and len(bf)> 20:
                axe[0].text(date_x[i],pr[i]-3.5,'Done', color = 'whitesmoke',horizontalalignment='center',fontsize=7,alpha=5)
            elif bf[i] == 1.0 and len(bf) < 21:
                axe[0].text(date_x[i],pr[i]-3.5,'Done', color = 'whitesmoke',horizontalalignment='center',fontsize=9,alpha=5)
            else:
                pass
    except:
        pass

    # Monthly Average
    monthavg = (np.sum(mon['Total'])/len(mon['Total']))*100
    totmed = np.sum(mon['Meditation'])
    totread = np.sum(mon['Reading'])
    axe[0].text(0,1.1,'Total Average: %.2f'% monthavg +'%', color = 'k',fontweight = 'bold',
                            fontsize = 13, alpha = .83, transform= axe[0].transAxes)
    axe[0].text(.37,1.1,'Total Meditation: %d'% totmed+'min', color = 'orange',fontweight = 'bold',
                            fontsize = 13, alpha = .5, transform= axe[0].transAxes)
    axe[0].text(.76,1.1,'Total Reading: %d'% totread+'min', color = 'red',fontweight = 'bold',
                            fontsize = 13, alpha = .5, transform= axe[0].transAxes)
    
    # Write in minutes for Personal Reading > 100
    c = 0
    for i in mon['Reading']:
        if i > 130:
            axe[0].text(date_x[c], 90, int(i), horizontalalignment = 'center', color = 'white')
        c += 1
    # Write in Percentage 
    for j in range(len(tt)):
        # Special Events
        try:
            events = []
            for i in mon['Events']:
                try:
                    int(i)
                    events.append('')
                except:
                    if ' ' in i:
                        i = i.replace(' ','\n')
                    else:
                        pass
                    events.append(i)
            # Special Events
            axe[0].text(date_x[j], round(tt[j]*100,2)+5.7 ,events[j],horizontalalignment = 'center',color = 'blue' ,fontsize=7.5, alpha=.7)
        except:
            pass
        
        axe[0].text(date_x[j], round(tt[j]*100,2)+2, round(tt[j]*100,1), horizontalalignment = 'center' ,color = 'k')
        
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    try: 
        fig.suptitle('Month: %s '%(mon['Date'].iloc[-1][0:3]).strip('/\"'), fontsize = 16, fontweight = 'bold')
    except:
        fig.suptitle('Month: %s '%(mon['Name'].iloc[-1][0:3]).strip('/\"'), fontsize = 16, fontweight = 'bold')
    if os.name == 'posix':
        plt.savefig('/Volumes/Programming/Personal/progress/jpg files/Monthly Evaluation/Month.jpg', format = 'jpg'
                , dpi=1000, bbox_inches = 'tight')
    else:
        plt.savefig('D:\Personal\progress\jpg files\Monthly Evaluation\Month.jpg', format = 'jpg'
                , dpi=300, bbox_inches = 'tight')


#%%
'''
                            [Monthly Improvement]
'''

def improvement(M):
    c = 0
    for T in range(len(M)):
        a = []
        b = []
        try:
            for j in M[T]['Drink']:
                if c == 0:
                    if j == 1.0:
                        a.append(j)
                    dk = len(a)
                else:
                    if j == 1.0:
                        b.append(j)
        except KeyError:
            if c == 0:
                dk = len('')
            else:
                b =[]

        dkk = len(b)
        dd = len(b)-dk
        if len(b)-dk > 0:
            dd = '+'+str(len(b)-dk)      
        
        tot_sc = 0
        for j in list(M[T]['Screen time']):
            if c == 0:
                tot_sc += j
                st1 = tot_sc
                st1 = round(st1/60,2)
            else:
                tot_sc += j
                st2 = tot_sc
                st2 = round(st2/60,2)
                dst = round(st2-st1,2)
                if dst > 0:
                    dst = '+'+str(dst)

        a = []
        b = []
        try:
            for j in list(M[T]['Reading']):
                if c ==0:
                    a.append(j)
                    rd = sum(a)    
                else:
                    b.append(j)
        except KeyError:
            if c==0:
                rd = len('')
            else:
                b = 0
        rdd = sum(b)
        dr = round(sum(b)-rd)
        if sum(b)-rd > 0:
            dr = '+'+str(round(sum(b)-rd))
        
        # Work Done 
        a = []
        b = []
        for j in list(M[T]['Work done %']):
            if c ==0:
                if j >= .235:
                    a.append(j)
                wd = len(a)    
            else:
                if j >= .235:
                    b.append(j)
        dw = len(b)-wd
        wdd = round(len(b),2)
        dw = len(b)-wd
        if len(b)-wd > 0:
            dw = '+'+str(len(b)-wd)
    
        tt = np.array(list(M[T]['Total']))
        tt_mean = np.average(tt)
        tt_min = min(tt)
        tt_max = max(tt)
        dt = round((np.mean(np.array(list(M[T]['Total'])))-np.mean(np.array(list(reversed(M[0]['Total'])))))*100,2)
        if dt > 0:
            dt = '+'+str(dt)
        
        if 'Date' in M[T]:
            day = np.array(list(M[T]['Date']))
        else:
            day = np.array(list(M[T]['Name']))
        if '/' in day[0][0:2]:
            month = int(day[0][0:1])
        else:
            month = int(day[0][0:2])
            
        # total evaluations
        if c == 0:
            total_e = len(M[T]['Name'])
        else:
            td = total_e
            total_e = len(M[T]['Name'])
            if total_e-td > 0:
                td = '+'+ str(round(total_e-td))
            else:
                td = round(total_e-td)
        
        # Meditation
        if c == 0:
            med = np.array(M[T]['Meditation'])
            med = np.sum(med)
        else:
            md = med
            med = np.array(M[T]['Meditation'])
            med = np.sum(med)
            if med-md > 0:
                md = '+'+str(round(med-md))
            else:
                md = round(med-md)
        
        # Rise time
        on_time = []
        for i in M[T]['Rise time']:
            if i <= 0:
                on_time.append(i)
        if c== 0:
            rt = len(on_time)
        else:
            drt = rt
            rt = len(on_time)
            if rt-drt > 0:
                drt = '+'+str(rt-drt)
            else:
                drt = rt-drt
        
        # Books finished
        books = []
        try:
            for i in M[T]['Books finished']:
                if i == 1:
                    books.append(i)
        except KeyError:
            books = []
        if c == 0:
            bb = len(books)
        else:
            db = bb
            bb = len(books)
            if bb-db > 0:
                db = '+'+str(round(bb-db,2))
            else:
                db = bb-db
        # ***Difference***
        if c == 1:
            comMonth = ('\nMonth : %s\n\n\
            Monthly Report     |          last month\n\
            -----------------------------------------\n\
            * Days woke up on time   : %d    %s\n\n\
            * More than two beers    : %s    %s\n\n\
            * Total Reading time     : %s m  %s\n\n\
            * Books finished         : %d    %s\n\n\
            * Productive days        : %s    %s\n\n\
            * Total Meditation       : %d m  %s\n\n\
            * Total Screen Time      : %.2f h %s\n\n\n\
            *TOTAL*\n\
            -----------------------------------------\n\
            MIN     : %s\n\
            MAX     : %s\n\
            AVERAGE : %s         %s\n\n\
            --> TOTAL Evaluations  : %d    %s  \n\
            ' % (month, rt, str.rjust(str(drt),7),dkk,str.rjust(str(dd),7), 
            round(rdd), str.rjust(str(dr),6),bb,
            str.rjust(str(db),7),wdd, str.rjust(str(dw),7), 
            med, str.rjust(str(md),8), st2,str(dst),
            round(tt_min*100,2), round(tt_max*100,2), round(tt_mean*100,2),
            str.rjust(str(dt),17),total_e, str.rjust(str(td),6)
            ))
            print(comMonth)
        else:
            print('\nMonth : %s\n\n\
            Monthly Report             \n\
            -----------------------------------------\n\
            * Days woke up on time   : %d\n\n\
            * More than 2 beers      : %s\n\n\
            * Total Reading time     : %s m\n\n\
            * Books finished         : %d\n\n\
            * Productive days        : %s\n\n\
            * Total Meditation       : %d m\n\n\
            * Total Screen Time      : %.2f h\n\n\n\
            *TOTAL*\n\
            -----------------------------------------\n\
            MIN     : %s\n\
            MAX     : %s\n\
            AVERAGE : %s\n\n\
            --> TOTAL Evaluations  : %d    \n\
            ' % (month, rt, dk, round(rd), bb,wd,med,st1, round(tt_min*100,2), 
            round(tt_max*100,2), round(tt_mean*100,2), total_e))
        c +=1
        
    return comMonth


#%%

'''
                    [Plot Evaluation by Month (Dependent variables)]

'''

def DEP_n(x,n):
    factors_n = [x]
    dep_cor = pCor.PearsonTest(mon.all_data()[0])[0]
    all_dat = mon.all_data()[0]
        # Originally: dep_cor(all_dat)
        # dep_cor: pCor.PearsonTest[0]
        # all_dat: pRd.read_All()[0]
    for i in dep_cor: 
        i = i.split(' & ')                          
        com1 = i[0].strip('Cor TEST :')             
        com2 = i[1]
        if x.strip('Cor TEST :') == com1:
            factors_n.append(com2)
    new_dic = {}
    for j in factors_n:
        dat = np.array(all_dat[j])
        new_val = []
        ave = []
        c = 0
        d = 0
        for k in dat:
            if c < n:
                ave.append(k)
            elif c == n:
                ave.append(k)
                average = round(np.average(ave),2)
                new_val.append(average)
                ave = []
                c = 0
            if d == len(dat)%n:
                ave.append(k)
                average = round(np.average(ave),2)
                new_val.append(average)
            c += 1
            d += 1
        
        new_dic[j] = new_val

    # Find how many graphs you want
    rows = []
    for i in dep_cor:
        i = i.split(' & ')
        com1 = i[0].strip('Cor TEST :')
        com2 = i[1]
        if x.strip('Cor TEST :') == com1:
            rows.append('(:')
    fig, axe = plt.subplots(len(rows),1,figsize=(13,10), sharex=True)
    length = len(new_dic[x])
    x_positions = np.arange(0,length)
    main = np.average(new_dic[x][:])
    if main > 200:
        main = np.array(new_dic[x])/300     
    elif 50 < main < 200:
        main = np.array(new_dic[x])/40
    elif 8 < main < 20:
        main = np.array(new_dic[x])/6   
    elif 1 < main < 8:
        main = np.array(new_dic[x])/3
    else:
        main = np.array(new_dic[x])*6
    c = 0
    for i in dep_cor:
        i_v = i
        i = i.split(' & ')
        com1 = i[0].strip('Cor TEST :')
        com2 = i[1]
        if x.strip('Cor TEST :') == com1:
            title = com2
            range_fac = np.average(new_dic[title])
            if range_fac > 200:
                factor = np.array(new_dic[title])/300   
            elif 50 < range_fac < 200:
                factor = np.array(new_dic[title])/100
            elif 8 < range_fac < 20:
                factor = np.array(new_dic[title])/10   
            elif 1 < range_fac < 8:
                factor = np.array(new_dic[title])/4
            else:
                factor = np.array(new_dic[title])*3
            if len(x_positions) != len(factor):
                x_positions = np.arange(0,len(factor))
            axe[c].plot(x_positions, factor,'m', lw=2)
            axe[c].set_xlabel(i[-1]+'\nP-value = %s, Stat = %s'%(dep_cor[i_v][0],dep_cor[i_v][1]), fontweight = 'bold', color = 'm')
            if n > 3:
                for i in range(len(x_positions)):
                    if len(rows) < 4:
                        axe[c].text(x_positions[i], factor[i]+.15, round(factor[i],2), horizontalalignment = 'center', color = 'm')
                    else:
                        axe[c].text(x_positions[i], factor[i]+.5, round(factor[i],2), horizontalalignment = 'center', color = 'm')
                    
            if c== 0:
                axe[c].bar(x_positions, main, color = 'orange', alpha = .5, label = x, width = .5)
            else:
                axe[c].bar(x_positions, main, color = 'orange', alpha = .5, width = .5)
            c += 1
    fig.tight_layout(w_pad = 3)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.legend()
    fig.suptitle(x+ ' ['+str(n)+' days]', fontsize = 15, fontweight='bold')
    
    # x, y super labels
    fig.subplots_adjust(bottom=.17, left = .04)
    fig.text(0.5, 0.06, '\nDays', ha='center', fontsize=13, fontweight = 'bold')
    fig.text(0, 0.5, 'Adjusted values', va='center', rotation='vertical', fontsize=13, fontweight = 'bold')
    
    try:
        plt.savefig('/Volumes/Programming/Personal/progress/jpg files/Overall/Specific Correlation[day].jpg', format = 'jpg'
                , dpi=1000, bbox_inches = 'tight')
    except FileNotFoundError:
        plt.savefig('D:\Personal\progress\jpg files\Overall\Specific Correlation[day].jpg', format = 'jpg'
                , dpi=1000, bbox_inches = 'tight')