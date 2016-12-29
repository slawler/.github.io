# -*- coding: utf-8 - Python 3.5.1 *-
"""
Description: Grab Time Series data From USGS Web Service
Input(s)   : USGS Gages, Parameters
Output(s)  : .rdb time series files
slawler@dewberry.com
Created on Tue Apr 19 15:08:33 2016
"""
# Import libraries

import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
from matplotlib.font_manager import FontProperties


def GetTimeSeries(gage, start, stop ):
    #parameter  = ["00060","00065"]                       # Try Flow first    
    parameter  = ["00065","00060"]                       # Try Stage First                    
    dformat    = "json"                                  # Data Format  
    url        = 'http://waterservices.usgs.gov/nwis/iv' # USGS API
         
    
    # Format Datetime Objects for USGS API
    first    =  datetime.date(start).strftime('%Y-%m-%d')
    last     =  datetime.date(stop).strftime('%Y-%m-%d') 
    
    
    # Ping the USGS API for data
    try:
        params = OrderedDict([('format',dformat),('sites',gage),('startDT',first), 
                    ('endDT',last), ('parameterCD',parameter[0])])  
        
        r = requests.get(url, params = params) 
        print("\nRetrieved Data for USGS Gage: ", gage)
        data = r.content.decode()
        d = json.loads(data)
        mydict = dict(d['value']['timeSeries'][0])
        
    except:
        params = OrderedDict([('format',dformat),('sites',gage),('startDT',first), 
                    ('endDT',last), ('parameterCD',parameter[1])])  
        
        r = requests.get(url, params = params) 
        print("\nRetrieved Data for USGS Gage: ", gage)
        data = r.content.decode()
        d = json.loads(data)
        mydict = dict(d['value']['timeSeries'][0])
    
    if params['parameterCD'] == '00060':
        obser = "StreamFlow"
    else:
        obser = "Stage"
        
    
    # Great, We can pull the station name, and assign to a variable for use later:
    SiteName = mydict['sourceInfo']['siteName']
    print('\n', SiteName)
    
    # After reveiwing the JSON Data structure, select only data we need: 
    tseries = d['value']['timeSeries'][0]['values'][0]['value'][:]
    
    
    # Create a Dataframe, format Datetime data,and assign numeric type to observations
    df = pd.DataFrame.from_dict(tseries)
    df.index = pd.to_datetime(df['dateTime'],format='%Y-%m-%d{}%H:%M:%S'.format('T'))
    
    df['UTC Offset'] = df['dateTime'].apply(lambda x: x.split('-')[3][1])
    df['UTC Offset'] = df['UTC Offset'].apply(lambda x: pd.to_timedelta('{} hours'.format(x)))
    
    df.index = df.index - df['UTC Offset']
    df.value = pd.to_numeric(df.value)
    
    
    # Get Rid of unwanted data, rename observed data
    df = df.drop('dateTime', 1)
    df.drop('qualifiers',axis = 1, inplace = True)
    df.drop('UTC Offset',axis = 1, inplace = True)
    df = df.rename(columns = {'value':obser})

    return df



# Enter Desired Data Download Period
y0, m0 ,d0 = 2004, 10, 6     # Start date (year, month, day)
y1, m1 ,d1 = 2017, 1, 1      

# Create Datetime Objects
start     = datetime(y0, m0, d0,0)    
stop      = datetime(y1, m1 ,d1,0)    


gage       = "01651750"     # 'Anacostia, DS Tidal Gage Max'
df_ANAD2 = GetTimeSeries(gage, start, stop)
max_anad = df_ANAD2.idxmax()[0]

gage       = "01649500"      #'Anacostia, NE Branch'
df_RVDM2 = GetTimeSeries(gage, start, stop)
max_rvdm = df_RVDM2.idxmax()[0]

gage       = "01651000"      # 'Anacostia, NW Branch'
df_ACOM2 = GetTimeSeries(gage, start, stop)
max_acom = df_ACOM2.idxmax()[0]


#---Set Plotting Window & Station Max ID
curr_plot = 'Anacostia, DS Tidal Gage Max'
pltfrom = max_anad- timedelta(days = 2)
pltto = max_anad + timedelta(days = 2)



curr_plot = 'Anacostia, NW Branch'
pltfrom = max_acom- timedelta(days = 2)
pltto = max_acom + timedelta(days = 2)


plt.interactive(False)
curr_plot = 'Anacostia, NE Branch'
pltfrom = max_rvdm- timedelta(days = 2)
pltto = max_rvdm + timedelta(days = 2)



#--------PLOT
fig, ax = plt.subplots(figsize=(14,8))

#--Plot medium_range NWM
x0 = df_ANAD2[pltfrom :pltto].index
y0 = df_ANAD2[pltfrom :pltto]['Stage']

x1 = df_RVDM2[pltfrom :pltto].index
y1 = df_RVDM2[pltfrom :pltto]['Stage']

x2 = df_ACOM2[pltfrom :pltto].index
y2 = df_ACOM2[pltfrom :pltto]['Stage']


ax.scatter(x0,y0, color='black', label='Anacostia, DS Tidal Gage')
ax.plot(x1,y1, color='r', label='Anacostia, NE Branch')
ax.plot(x2,y2, color='b', label='Anacostia, NW Branch')


ax.set_xlim(pltfrom,pltto)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, scatterpoints = 1)
ax.legend(loc='best', fontsize = 'small')


#--Write in Labels

plt.ylabel('Stage (ft)')
plt.xlabel(pltto.year)
plt.title('Local Max: {}'.format(curr_plot))
#plot_name = os.path.join(root_dir, 'Levee_Seg_{}.png'.format(segment))
    
plt.grid(True)
plt.gca().xaxis.set_major_formatter(DateFormatter('%I%p\n%a\n%b%d'))
plt.gca().xaxis.set_major_locator(HourLocator(byhour=range(24), interval=12))       
plt.savefig(curr_plot+'.png', dpi=600) 
        
