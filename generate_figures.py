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

# Block 3 - Calculate ROSI
worldwide_hosts = 1e9
company_hosts = 100
z_value = 2.57  # Z value for 99% confidence intervals

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
print(date_histogram)
print(len(date_histogram))

color = 'cornflowerblue'
fig, ax = plt.subplots()
ax.plot(np.arange(len(date_histogram)), date_histogram["Expectation"], color=color)
ax.fill_between(
    np.arange(len(date_histogram)),
    date_histogram["Expectation"],
    y2=date_histogram["Expectation"] + date_histogram["Std"],
    alpha=0.4,
    color=color
)
ax.fill_between(
    np.arange(len(date_histogram)),
    date_histogram["Expectation"],
    y2=date_histogram["Expectation"] - date_histogram["Std"],
    alpha=0.4,
    color=color
)
ax.set_xticks(np.arange(len(date_histogram)))
ax.set_xticklabels(date_histogram["Date"], rotation=40)
ax.set_xlabel('Date')
ax.set_ylabel('Amount of infected machines')
plt.show()
