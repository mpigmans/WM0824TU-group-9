import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pycountry
import numpy as np

# Data columns are as follows:
# IP_Address ; Autonomous_System ; Country ; ASN ; Date_First_Seen
data = pd.read_csv("data.csv", sep=";", parse_dates=["Date_First_Seen"])

# Load country internet data to normalize over size
users_per_country = pd.read_csv("internet_users.csv")
countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_2

# Figure 1: Amount of infected hosts by country
top_count = 20

count_per_country_date = (
    data.groupby("Country").size().reset_index(name="Infected Hosts")
)
users_per_country = users_per_country.rename(columns={"Country or Area": "Country"})
users_per_country["Country"] = users_per_country["Country"].apply(
    lambda x: countries.get(x, "Unknown code")
)
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

# Bar plot top countries by mirai infected hosts normalized by internet users
sorted_countries = combined_data.sort_values(by="Internet Users", ascending=False)
sorted_countries = sorted_countries.head(50)
sorted_countries = sorted_countries.sort_values(
    by="Infected Hosts / Internet Users", ascending=False
)
top_countries = sorted_countries.head(top_count)
sns.barplot(
    data=top_countries,
    x="Country",
    y="Infected Hosts / Internet Users",
    palette="GnBu_d",
)
plt.tight_layout()
plt.savefig("figures/infected_hosts_by_country")
plt.close()

# Scatter plot comparing country internet usage with amount of mirai infected hosts
sorted_countries = combined_data.sort_values(by="Internet Users", ascending=False)
sorted_countries = sorted_countries.head(15)
ax = sns.scatterplot(
    data=sorted_countries,
    x="Internet Users",
    y="Infected Hosts",
    hue="Country",
    palette="GnBu_d",
)
ax.set(xscale="log", yscale="log")
plt.tight_layout()
plt.savefig("figures/infected_hosts_by_country_scatter")
plt.close()

# Figure 2: Amount of infected hosts over time
dates = data["Date_First_Seen"]
data_month_year = dates.apply(lambda date: (date.year, date.month))
date_histogram = data_month_year.value_counts().sort_index().to_frame()
date_histogram["Date"] = date_histogram.index
date_histogram.columns = ["Infected Hosts", "Date"]
date_histogram["Date"] = date_histogram["Date"].apply(lambda x: "{}-{}".format(*x))
ax = sns.lineplot(
    data=date_histogram,
    x="Date",
    y="Infected Hosts",
    palette="GnBu_d",
    marker="o",
    sort=False,
)
plt.xticks(rotation=35)
plt.tight_layout()
plt.savefig("figures/infected_hosts_over_time")
plt.close()

# Figure 3: Hosts per country and time
data["Date_First_Seen"] = data["Date_First_Seen"].apply(
    lambda date: (date.year, date.month)
)
count_per_country_date = (
    data.groupby(["Country", "Date_First_Seen"]).size().reset_index(name="Hosts")
)
users_per_country.drop(
    columns=["Population", "Rank", "Percentage", "Rank.1"], inplace=True
)
users_per_country["Internet Users"] = users_per_country["Internet Users"].apply(
    lambda x: x.replace(",", "")
)
users_per_country["Internet Users"] = pd.to_numeric(users_per_country["Internet Users"])
users_per_country = users_per_country.sort_values(
    by="Internet Users", ascending=False
).head(25)
combined_data = pd.merge(
    count_per_country_date, users_per_country, how="inner", on="Country"
)
combined_data["Infected Hosts / Internet Users"] = (
    combined_data["Hosts"] / combined_data["Internet Users"]
)
combined_data.drop(columns=["Hosts", "Internet Users"], inplace=True)
combined_data.rename(columns={"Date_First_Seen": "Date First Detected"}, inplace=True)
data_country_time = pd.pivot_table(
    combined_data,
    index="Date First Detected",
    columns="Country",
    values="Infected Hosts / Internet Users",
    fill_value=0,
)
data_country_time.index = ["{}-{}".format(*x) for x in data_country_time.index]
sns.heatmap(data_country_time, cmap="GnBu")
plt.tight_layout()
plt.savefig("figures/infected_hosts_by_country_and_time")
plt.close()


# Block 3 - plot infections per IP block (by IP prefix)
prefixes_to_plot = {
    "4": "CenturyLink",
    "12": "AT&T",
    "17": "Apple",
    "19": "Ford",
    "38": "PSINet",
    "44": "Amateur Radio Digital Communications",
    "48": "Prudential Securities",
    "56": "US Postal Service",
    "73": "Comcast",
}
data_date_ip = data[["Date_First_Seen", "IP_Address"]].copy(deep=True)
data_date_ip["IP_Prefix"] = data_date_ip["IP_Address"].apply(
    lambda ip: ip.split(".")[0]
)
data_date_ip.drop(columns=["IP_Address"], inplace=True)
data_date_ip = data_date_ip[data_date_ip["IP_Prefix"].isin(prefixes_to_plot.keys())]
data_date_ip["IP_Prefix"] = data_date_ip["IP_Prefix"].map(prefixes_to_plot)
date_ip_sizes = (
    data_date_ip.groupby(["Date_First_Seen", "IP_Prefix"])
    .size()
    .reset_index(name="Count")
)
date_ip_sizes["Date"] = date_ip_sizes["Date_First_Seen"].apply(
    lambda x: "{}-{}".format(*x)
)
sns.lineplot(data=date_ip_sizes, x="Date", y="Count", hue="IP_Prefix")
plt.xticks(rotation=35)
plt.tight_layout()
plt.savefig("figures/infected_hosts_over_time_by_ip_block")
plt.close()

# Block 3 - plot infections per autonomous system
print(data["ASN"].value_counts())
# asns_to_plot = {
#     'AS8708': 'AS8708',
#     'AS4766': 'AS4766',
#     'AS4134': 'AS4134',
#     'AS4837': 'AS4837',
#     'AS8452': 'AS8452',
# }
asns_to_plot = {
    "AS209": "CenturyLink Communications",
    "AS7018": "AT&T Services",
    "AS7922": "Comcast Cable Communications",
}
isp_to_size = {
    "CenturyLink Communications": 20809984,
    "AT&T Services": 83883008,
    "Comcast Cable Communications": 71195904,
}  # Data from https://ipinfo.io/
data_date_asn = data[["Date_First_Seen", "ASN"]].copy(deep=True)
data_date_asn = data_date_asn[data_date_asn["ASN"].isin(asns_to_plot.keys())]
data_date_asn["ASN"] = data_date_asn["ASN"].map(asns_to_plot)
date_asn_sizes = (
    data_date_asn.groupby(["Date_First_Seen", "ASN"]).size().reset_index(name="Count")
)
date_asn_sizes["Infected / Total Addresses"] = date_asn_sizes["Count"] / date_asn_sizes[
    "ASN"
].map(isp_to_size)
date_asn_sizes["Infected / Million Total Addresses"] = (
    date_asn_sizes["Infected / Total Addresses"] * 1000000
)
date_asn_sizes["Date"] = date_asn_sizes["Date_First_Seen"].apply(
    lambda x: "{}-{}".format(*x)
)
print(date_asn_sizes)
sns.lineplot(
    data=date_asn_sizes,
    x="Date",
    y="Infected / Million Total Addresses",
    hue="ASN",
    sort=False,
)
plt.xticks(rotation=35)
plt.tight_layout()
plt.savefig("figures/infected_hosts_over_time_by_asn")
plt.close()

# Calculate comcast devices and ROSI
gb_per_device_per_month = 74120
gb_per_device_per_month_std = 23800
cost_per_gb = 0.002
attacking_device_fraction = 0.087
attacking_device_fraction_std = 0.025
color = "cornflowerblue"

asns_to_plot = {"AS7922": "Comcast Cable Communications"}
data_date_asn = data[["Date_First_Seen", "ASN"]].copy(deep=True)
data_date_asn = data_date_asn[data_date_asn["ASN"].isin(asns_to_plot.keys())]
data_date_asn["ASN"] = data_date_asn["ASN"].map(asns_to_plot)
date_asn_sizes = (
    data_date_asn.groupby(["Date_First_Seen", "ASN"])
    .size()
    .reset_index(name="Infected Devices")
)
date_asn_sizes["Date"] = date_asn_sizes["Date_First_Seen"].apply(
    lambda x: "{}-{}".format(*x)
)
print(date_asn_sizes)
sns.lineplot(data=date_asn_sizes, x="Date", y="Infected Devices", hue="ASN", sort=False)
plt.xticks(rotation=35)
plt.tight_layout()
plt.savefig("figures/infected_comcast_hosts_over_time")
plt.close()

date_asn_sizes["Cost Expectation"] = (
    date_asn_sizes["Infected Devices"] * attacking_device_fraction * gb_per_device_per_month * cost_per_gb
)
date_asn_sizes["Cost Upper"] = (
    date_asn_sizes["Infected Devices"]
    * (attacking_device_fraction + attacking_device_fraction_std)
    * (gb_per_device_per_month + gb_per_device_per_month_std)
    * cost_per_gb
)
date_asn_sizes["Cost Lower"] = (
    date_asn_sizes["Infected Devices"]
    * (attacking_device_fraction - attacking_device_fraction_std)
    * (gb_per_device_per_month - gb_per_device_per_month_std)
    * cost_per_gb
)

fig, ax = plt.subplots()
ax.plot(np.arange(len(date_asn_sizes)), date_asn_sizes["Cost Expectation"], color=color)
ax.fill_between(
    np.arange(len(date_asn_sizes)),
    date_asn_sizes["Cost Expectation"],
    y2=date_asn_sizes["Cost Upper"],
    alpha=0.4,
    color=color,
)
ax.fill_between(
    np.arange(len(date_asn_sizes)),
    date_asn_sizes["Cost Expectation"],
    y2=date_asn_sizes["Cost Lower"],
    alpha=0.4,
    color=color,
)
ax.set_xticks(np.arange(len(date_asn_sizes)))
ax.set_xticklabels(date_asn_sizes["Date"], rotation=40, ha="right")
ax.set_xlabel("Date")
ax.set_ylabel("Cost (USD)")
plt.tight_layout()
plt.savefig("figures/comcast_costs")
plt.close()

print("Expected loss:", date_asn_sizes.loc[0:18]["Cost Expectation"].sum())
print("Upper loss:", date_asn_sizes.loc[0:18]["Cost Upper"].sum())
print("Lower loss:", date_asn_sizes.loc[0:18]["Cost Lower"].sum())

# Block 3 - Calculate ROSI
worldwide_hosts = 1e9
company_hosts = 100
costs_mean = 2161409
costs_std = 1400000

date_histogram.reset_index(inplace=True, drop=True)
date_histogram["Infection Likelihood"] = (
    date_histogram["Infected Hosts"] / worldwide_hosts
)
date_histogram["Expectation"] = date_histogram["Infection Likelihood"] * company_hosts
date_histogram["Std"] = np.sqrt(
    (
        date_histogram["Infection Likelihood"]
        * (1 - date_histogram["Infection Likelihood"])
    )
    / company_hosts
)
date_histogram["Upper"] = date_histogram["Expectation"] + date_histogram["Std"]
date_histogram["Lower"] = date_histogram["Expectation"] - date_histogram["Std"]

fig, ax = plt.subplots()
ax.plot(np.arange(len(date_histogram)), date_histogram["Expectation"], color=color)
ax.fill_between(
    np.arange(len(date_histogram)),
    date_histogram["Expectation"],
    y2=date_histogram["Upper"],
    alpha=0.4,
    color=color,
)
ax.fill_between(
    np.arange(len(date_histogram)),
    date_histogram["Expectation"],
    y2=date_histogram["Lower"],
    alpha=0.4,
    color=color,
)
ax.set_xticks(np.arange(len(date_histogram)))
ax.set_xticklabels(date_histogram["Date"], rotation=40)
ax.set_xlabel("Date")
ax.set_ylabel("Amount of infected machines")
plt.tight_layout()
plt.savefig("figures/affected_machines")
plt.close()

# Plot the cost distribution over time
date_histogram["Cost Expectation"] = date_histogram["Expectation"] * costs_mean
date_histogram["Cost Upper"] = date_histogram["Upper"] * (costs_mean + costs_std)
date_histogram["Cost Lower"] = date_histogram["Lower"] * (costs_mean - costs_std)

fig, ax = plt.subplots()
ax.plot(np.arange(len(date_histogram)), date_histogram["Cost Expectation"], color=color)
ax.fill_between(
    np.arange(len(date_histogram)),
    date_histogram["Cost Expectation"],
    y2=date_histogram["Cost Upper"],
    alpha=0.4,
    color=color,
)
ax.fill_between(
    np.arange(len(date_histogram)),
    date_histogram["Cost Expectation"],
    y2=date_histogram["Cost Lower"],
    alpha=0.4,
    color=color,
)
ax.set_xticks(np.arange(len(date_histogram)))
ax.set_xticklabels(date_histogram["Date"], rotation=40)
ax.set_xlabel("Date")
ax.set_ylabel("Costs (EUR)")
plt.tight_layout()
plt.savefig("figures/costs_machines")
plt.close()

print("Expected loss:", date_histogram.loc[0:18]["Cost Expectation"].sum())
print("Upper loss:", date_histogram.loc[0:18]["Cost Upper"].sum())
print("Lower loss:", date_histogram.loc[0:18]["Cost Lower"].sum())
