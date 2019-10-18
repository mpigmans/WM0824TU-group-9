import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pycountry
import numpy as np
import datetime
from scipy.stats import pearsonr, spearmanr
import statsmodels.formula.api as smf

# Set parameters for plot:
start_date = datetime.datetime(2018, 6, 1)
end_date = datetime.datetime(2018, 7, 1)

# Data columns are as follows:
# IP_Address ; Autonomous_System ; Country ; ASN ; Date_First_Seen
data = pd.read_csv("data.csv", sep=";", parse_dates=["Date_First_Seen"])
users_per_country = pd.read_csv("internet_users.csv")
idi_data = pd.read_csv("idi_codes.csv")
crime_data = pd.read_csv("crime_index.csv")

# Combine datasets
data = data.loc[
    (data["Date_First_Seen"] > start_date) & (data["Date_First_Seen"] < end_date)
]
data.rename(columns={"Date_First_Seen": "Date First Detected"})
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
combined_data["Infections"] = (
    combined_data["Infected Hosts"] / combined_data["Internet Users"]
)

# Load GCI data
gci_data = pd.read_csv("gci.csv")
gci_data = gci_data.rename(columns={"Member State": "Country", "Score": "GCI"})
gci_data = gci_data.drop(columns=["Global Rank"])
combined_data = pd.merge(combined_data, gci_data, on="Country", how="inner")
combined_data = pd.merge(combined_data, crime_data, on="Country", how="inner")
combined_data = pd.merge(combined_data, idi_data, on="Country", how="inner")

# Make infections normal distribution using logarithm
print(combined_data)
combined_data["Infections"] = combined_data["Infections"].apply(np.log10)
print(combined_data)
correlation, p = pearsonr(combined_data["Infections"], combined_data["IDI"])
print("IDI Correlation:", correlation, f"p={round(p, 4)}")
correlation, p = spearmanr(combined_data["Infections"], combined_data["IDI"])
print("IDI Spearman:", correlation, f"p={round(p, 4)}")
sns.jointplot(x="IDI", y="Infections", data=combined_data, kind="reg")
plt.tight_layout()
plt.savefig("figures/correlation_idi")
plt.close()

correlation, p = pearsonr(combined_data["Infections"], combined_data["GCI"])
print("GCI Correlation:", correlation, f"p={round(p, 4)}")
correlation, p = spearmanr(combined_data["Infections"], combined_data["GCI"])
print("GCI Spearman:", correlation, f"p={round(p, 4)}")
sns.jointplot(x="GCI", y="Infections", data=combined_data, kind="reg")
plt.tight_layout()
plt.savefig("figures/correlation_gci")
plt.close()

correlation, p = pearsonr(combined_data["Infections"], combined_data["Crime"])
print("Crime Correlation:", correlation, f"p={round(p, 4)}")
correlation, p = spearmanr(combined_data["Infections"], combined_data["Crime"])
print("Crime Spearman:", correlation, f"p={round(p, 4)}")
sns.jointplot(x="Crime", y="Infections", data=combined_data, kind="reg")
plt.tight_layout()
plt.savefig("figures/correlation_crime")
plt.close()

# Extract X and y from dataframe and fit OLS with combined metrics
formula = (
    "Infections ~ IDI + GCI + Crime + IDI * GCI + GCI * Crime + IDI * Crime + IDI * GCI * Crime"
)
print(smf.ols(formula, data=combined_data).fit().summary())
