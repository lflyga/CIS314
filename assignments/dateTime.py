"""
Author: L. Flygare
Description: import datetime module to display the current date and time
"""

import datetime

#gets current date and time
now = datetime.datetime.now()

print("Current date and time:")
#Year-Month-Day Hour:Minute:Second drops the milliseconds
print(now.strftime("%Y-%m-%d %H:%M:%S"))

#just the date
print("Today's date: ", now.date())

#just the time - no formatting so includes the milliseconds
print("Current time: ", now.time())