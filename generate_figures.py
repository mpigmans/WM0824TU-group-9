import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pycountry

# Data columns are as follows:
# IP_Address ; Autonomous_System ; Country ; ASN ; Date_First_Seen
data = pd.read_csv("data.csv", sep=";", parse_dates=["Date_First_Seen"])

# Load country internet data to normalize over size
users_per_country = pd.read_csv("internet_users.csv")
countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_2

# Figure 1: Amount of packets by country
top_count = 20

count_per_country = data.groupby("Country").size().reset_index(name="Packets")
users_per_country = users_per_country.rename(columns={"Country or Area": "Country"})
users_per_country["Country"] = users_per_country["Country"].apply(
    lambda x: countries.get(x, "Unknown code")
)
combined_data = pd.merge(
    count_per_country, users_per_country, on="Country", how="inner"
)
combined_data.drop(columns=["Population", "Rank", "Percentage", "Rank.1"], inplace=True)
combined_data["Internet Users"] = combined_data["Internet Users"].apply(
    lambda x: x.replace(",", "")
)
combined_data["Internet Users"] = pd.to_numeric(combined_data["Internet Users"])
combined_data["Packets / Users"] = (
    combined_data["Packets"] / combined_data["Internet Users"]
)

# Bar plot top countries by mirai packets normalized by internet users
sorted_countries = combined_data.sort_values(by="Internet Users", ascending=False)
sorted_countries = sorted_countries.head(50)
sorted_countries = sorted_countries.sort_values(by="Packets / Users", ascending=False)
top_countries = sorted_countries.head(top_count)
sns.barplot(data=top_countries, x="Country", y="Packets / Users", palette="GnBu_d")
plt.tight_layout()
plt.savefig("figures/packets_by_country")
plt.close()

# Scatter plot comparing country internet usage with amount of mirai packets
sorted_countries = combined_data.sort_values(by="Internet Users", ascending=False)
sorted_countries = sorted_countries.head(10)
ax = sns.scatterplot(
    data=sorted_countries, x="Internet Users", y="Packets", hue="Country"
)
ax.set(xscale="log", yscale="log")
plt.tight_layout()
plt.savefig("figures/packets_by_country_scatter")
