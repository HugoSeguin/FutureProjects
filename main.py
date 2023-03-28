#Import Data
import matplotlib.pyplot as plt
import fitbit
#pip install CherryPy
import cherrypy as cherrypy
# gather_keys_oauth2.py file needs to be in the same directory.
# also needs to install cherrypy: https://pypi.org/project/CherryPy/
# pip install CherryPy
import gather_keys_oauth2 as Oauth2
import pandas as pd
import datetime

# YOU NEED TO PUT IN YOUR OWN CLIENT_ID AND CLIENT_SECRET###################
### Goal is to collect Fitbit 2###############!!!!!!!!!!!!!
CLIENT_ID = '2388YN'
CLIENT_SECRET = '0598f271ffd8c0fb83611d79d4134daa'

#API Authorization
server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()
ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.' \
               'eyJhdWQiOiIyMzg4WU4iLCJzdWIiOiI5Tkc0M0IiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3N' \
               'fdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2' \
               'xlIiwiZXhwIjoxNjcwOTc3MjU4LCJpYXQiOjE2NzA5NDg0NTh9.fDcFwBwynPpRVJ3cn44fPYz_c6E_' \
               '5ozjmMK4yp7RXZE'
REFRESH_TOKEN = "353c354a8bbd8cca2f8b2dd13a251f9eea1bea515ed7758ac114ca841b46f3e9"

#5 a.) Get One day of Data##################################################################################################
# You will have to modify this
# depending on when you started to use a fitbit
#################################################Modify this as need a date actually collected data
oneDate = pd.datetime(year=2022, month=11, day=10)
help(auth2_client.intraday_time_series)
oneDayData = auth2_client.intraday_time_series('activities/heart',
base_date = oneDate,
detail_level = '1sec')
#oneDayData
df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
# Look at the first 5 rows of the pandas DataFrame
df.head()
# The first part gets a date in a string format of YYYY-MM-DD
filename = oneDayData['activities-heart'][0]['dateTime'] + '_intradata'

# Export file to csv
df.to_csv(filename + '.csv', index=False)
df.to_excel(filename + '.xlsx', index=False)


## 5b.) Get Multiple Days of Data
# startTime is first date of data that I want.
# You will need to modify for the date you want your data to start
startTime = pd.datetime(year=2022, month=11, day=21)
endTime = pd.datetime.today().date() - datetime.timedelta(days=20)
date_list = []
df_list = []
allDates = pd.date_range(start=startTime, end=endTime)

for oneDate in allDates:
    oneDate = oneDate.date().strftime("%Y-%m-%d")

oneDayData = auth2_client.intraday_time_series('activities/heart', base_date=oneDate, detail_level='1sec')

df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])

date_list.append(oneDate)

df_list.append(df)

final_df_list = []

for date, df in zip(date_list, df_list):
    if len(df) == 0:
        continue

df.loc[:, 'date'] = pd.to_datetime(date)

final_df_list.append(df)

final_df = pd.concat(final_df_list, axis=0)

## Optional Making of the data have more detailed timestamp (day and hour instead of day)
hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours=x))
minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes=x))
secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds=x))

# Getting the date to also have the time of the day
final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
final_df.tail()
filename = 'all_intradata'
final_df.to_csv(filename + '.csv', index=False)






###6.) Try to Graph Intraday Data
# this is bad as time is duplicated over many days fixing the date column will fix the problem
final_df.plot('time', 'value')
# The code below is not efficient as I call to_datetime twice
hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours=x))
minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes=x))
secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds=x))
# Getting the date to also have the time of the day
final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
# final_df['temp_value'] = final_df['value'] + random.randint(-2, 2)
# this fixed the problem.
final_df.plot('date', 'value')
plt.legend('')
## Looking at a couple days only.
startDate = pd.datetime(year=2019, month=12, day=24)
lastDate = pd.datetime(year=2019, month=12, day=27)

coupledays_df = final_df.loc[final_df.loc[:, 'date'].between(startDate, lastDate), :]
coupledays_df
# Just checking the number of the rows
coupledays_df.shape()
coupledays_df.plot('date', 'value')
plt.legend('')
fig, ax = plt.subplots(figsize=(10, 7))

# Taken from: https://stackoverflow.com/questions/16266019/python-pandas-group-datetime-column-into-hour-and-minute-aggregations
times = pd.to_datetime(coupledays_df['date'])
coupledays_df.groupby([times.dt.date, times.dt.hour]).value.mean().plot(ax=ax)

ax.grid(True,
axis = 'both',
zorder = 0,
linestyle = ':',
color = 'k')
ax.tick_params(axis='both', rotation=45, labelsize=20)
ax.set_xlabel('Date, Hour', fontsize=24)
ax.set_ylabel('Heart Rate', fontsize=24)
fig.tight_layout()
fig.savefig('coupledaysavergedByMin.png', format='png', dpi=300)



#####7.) Resting Heart Rate
# startTime is first date of data that I want.
# You will need to modify for the date you want your data to start
startTime = pd.datetime(year=2020, month=1, day=1)
endTime = pd.datetime.today().date() - datetime.timedelta(days=1)
date_list = []
resting_list = []

allDates = pd.date_range(start=startTime, end=endTime)

for oneDate in allDates:
    oneDate = oneDate.date().strftime("%Y-%m-%d")

oneDayData = auth2_client.intraday_time_series('activities/heart', base_date=oneDate, detail_level='1sec')

date_list.append(oneDate)

resting_list.append(oneDayData['activities-heart'][0]['value']['restingHeartRate'])
fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(date_list, resting_list)

# This is just making it so there isnt a grid line or text for every point
xtick_list = []
xticklabel_list = []
for index, label in enumerate(ax.get_xticklabels()):
    if index % 5 == 0:
        xticklabel_list.append(label)
        xtick_list.append(index)

ax.grid(True,
        axis='both',
        zorder=0,
        linestyle=':',
        color='k')
ax.tick_params(axis='both', labelsize=20)
ax.set_xticks(xtick_list)
ax.tick_params(axis='x', rotation=90, labelsize=20)
ax.set_xlim(0, index)
# ax.set_xticklabels(ax.get_xticklabels(),rotation = 45, rotation_mode="anchor", ha = 'right')
ax.set_xlabel('Date', fontsize=24)
ax.set_ylabel('Resting Heart Rate', fontsize=24)
fig.tight_layout()
fig.savefig('restingHR_graph.png', format='png', dpi=300)
resting_df = pd.DataFrame({'date': date_list, 'RHR': resting_list})
resting_df.head()



##8.) Get Sleep Data
startTime = pd.datetime(year=2020, month=1, day=5)
endTime = pd.datetime.today().date() - datetime.timedelta(days=1)
allDates = pd.date_range(start=startTime, end=endTime)
date_list = []
df_list = []
stages_df_list = []

allDates = pd.date_range(start=startTime, end=endTime)

for oneDate in allDates:
    oneDate = oneDate.date().strftime("%Y-%m-%d")

oneDayData = auth2_client.sleep(date=oneDate)

# get number of minutes for each stage of sleep and such.
stages_df = pd.DataFrame(oneDayData['summary'])

df = pd.DataFrame(oneDayData['sleep'][0]['minuteData'])

date_list.append(oneDate)

df_list.append(df)

stages_df_list.append(stages_df)

final_df_list = []

final_stages_df_list = []

for date, df, stages_df in zip(date_list, df_list, stages_df_list):
    if len(df) == 0:
        continue

df.loc[:, 'date'] = pd.to_datetime(date)

stages_df.loc[:, 'date'] = pd.to_datetime(date)

final_df_list.append(df)
final_stages_df_list.append(stages_df)

final_df = pd.concat(final_df_list, axis=0)

final_stages_df = pd.concat(final_stages_df_list, axis=0)
columns = final_stages_df.columns[~final_stages_df.columns.isin(['date'])].values
columns
pd.concat([final_stages_df[columns] + 2, final_stages_df[['date']]], axis=1)
# Export file to csv
final_df.to_csv('minuteSleep' + '.csv', index=False)
final_stages_df.to_csv('minutesStagesSleep' + '.csv', index=True)