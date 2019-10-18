import pandas as pd
import pycountry

def country_to_code(country_name):
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_2
    except LookupError:
        return country_name

# gci_data = pd.read_csv("gci.csv")
# gci_data['Member State'] = gci_data['Member State'].apply(country_to_code)
# gci_data.to_csv('gci_codes.csv', index=False)
# print(gci_data['Member State'].value_counts())

# gci_data = pd.read_csv("internet_users.csv")
# gci_data['Country or Area'] = gci_data['Country or Area'].apply(country_to_code)
# gci_data.to_csv('internet_users_codes.csv', index=False)
# print(gci_data['Country or Area'].value_counts())

# gci_data = pd.read_csv("gdp_per_capita.csv")
# # gci_data['Country'] = gci_data['Country'].apply(country_to_code)
# # gci_data = gci_data.drop(columns=['Country Code'])
# print(gci_data)
# gci_data = gci_data.dropna()
# print(gci_data)
# gci_data.to_csv('gdp_per_capita_codes.csv', index=False)
# # print(gci_data['Country'].value_counts())

gci_data = pd.read_csv("crime_index.csv",sep=';')
gci_data['Country'] = gci_data['Country'].apply(country_to_code)
gci_data.to_csv('crime_index_codes.csv', index=False)
print(gci_data['Country'].value_counts())