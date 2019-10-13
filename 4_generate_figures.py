import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pycountry
import numpy as np
import datetime
from scipy.stats import pearsonr

# Set parameters for plot:
start_date = datetime.datetime(2018, 1, 1)
end_date = datetime.datetime(2018, 12, 31)
# start_date = datetime.datetime(2010, 6, 1)
# end_date = datetime.datetime(2020, 6, 7)

# Data columns are as follows:
# IP_Address ; Autonomous_System ; Country ; ASN ; Date_First_Seen
data = pd.read_csv("data.csv", sep=";", parse_dates=["Date_First_Seen"])
users_per_country = pd.read_csv("internet_users.csv")
idi_data = pd.read_csv("idi_codes.csv")
gdp_data = pd.read_csv("gdp_per_capita.csv")

# Combine datasets
data = data.loc[(data['Date_First_Seen'] > start_date) & (data['Date_First_Seen'] < end_date)]
data.rename(columns={'Date_First_Seen': 'Date First Detected'})
count_per_country_date = (
    data.groupby("Country").size().reset_index(name="Infected Hosts")
)
users_per_country = users_per_country.rename(columns={"Country or Area": "Country"})
combined_data = pd.merge(
    count_per_country_date, users_per_country, on="Country", how="inner"
)
combined_data.drop(columns=["Population", "Rank", "Percentage", "Rank.1"], inplace=True)
combined_data["Internet Users"] = combined_data["Internet Users"].apply(
    lambda x: x.replace(",", "")
)
combined_data["Internet Users"] = pd.to_numeric(combined_data["Internet Users"])
combined_data["Infected Hosts / Internet Users"] = (
    combined_data["Infected Hosts"] / combined_data["Internet Users"]
)

# Load GCI data
gci_data = pd.read_csv("gci.csv")
gci_data = gci_data.rename(columns={"Member State": "Country", "Score": "Global Cybersecurity Index"})
gci_data = gci_data.drop(columns=["Global Rank"])
combined_data = pd.merge(
    combined_data, gci_data, on="Country", how="inner"
)
combined_data = pd.merge(
    combined_data, gdp_data, on="Country", how="inner"
)
combined_data = pd.merge(
    combined_data, idi_data, on="Country", how="inner"
)

correlation, p = pearsonr(combined_data['Infected Hosts / Internet Users'], combined_data['IDI'])
print('IDI Correlation:', correlation, f'p={round(p, 4)}')
sns.jointplot(x="IDI", y="Infected Hosts / Internet Users", data=combined_data, kind="reg")
plt.tight_layout()
plt.savefig('figures/correlation_idi')
plt.close()

correlation, p = pearsonr(combined_data['Infected Hosts / Internet Users'], combined_data['Global Cybersecurity Index'])
print('GCI Correlation:', correlation, f'p={round(p, 4)}')
sns.jointplot(x="Global Cybersecurity Index", y="Infected Hosts / Internet Users", data=combined_data, kind="reg")
plt.tight_layout()
plt.savefig('figures/correlation_gci')
plt.close()

correlation, p = pearsonr(combined_data['Infected Hosts / Internet Users'], combined_data['GDP per capita'])
print('GDP Correlation:', correlation, f'p={round(p, 4)}')
sns.jointplot(x="GDP per capita", y="Infected Hosts / Internet Users", data=combined_data, kind="reg")
plt.tight_layout()
plt.savefig('figures/correlation_gdp')
plt.close()
