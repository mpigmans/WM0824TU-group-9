import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Data columns are as follows:
# IP_Address ; Autonomous_System ; Country ; ASN ; Date_First_Seen
data = pd.read_csv('data.csv', sep=';', parse_dates=['Date_First_Seen'])

# Figure 1: Amount of packets by country
top_count = 20
count_per_country = data.groupby('Country').size().reset_index(name='Packets')
sorted_countries = count_per_country.sort_values(by='Packets', ascending=False)
top_countries = sorted_countries.head(top_count)
sns.barplot(data=top_countries, x='Country', y='Packets', palette='GnBu_d')
plt.savefig('figures/packets_by_country')

# Figure 3: Amount of packets over time
dates = data['Date_First_Seen']
data_month_year = dates.apply(lambda date: (date.year, date.month))
date_histogram = data_month_year.value_counts().sort_index().to_frame()
date_histogram['Date'] = date_histogram.index
date_histogram.columns = ['Packets', 'Date']
date_histogram['Date'] = date_histogram['Date'].apply(lambda x: '{}-{}'.format(*x))
ax = sns.barplot(data=date_histogram, x='Date', y='Packets', palette='GnBu_d')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
plt.tight_layout()
plt.savefig('figures/packets_over_time')