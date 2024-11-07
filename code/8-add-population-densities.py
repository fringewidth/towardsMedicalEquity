# %%
import pandas as pd

hospitals = pd.read_csv('../data/main/6-hospitals_anonymized.csv')
districts = pd.read_csv('../data/miscdistrict-density.csv')



# %%
hospitals['city'] = hospitals['City'].str.lower().str.replace('\r\n', '', regex=False).str.replace('\n', '', regex=False)
districts.drop(columns=['Unnamed: 0'], inplace=True)
districts['district'] = districts['District'].str.lower()


# %%
not_found = set()
for city in hospitals['city']:
    if city not in districts['district'].values:
        not_found.add(city.lower())
    
print(sorted(not_found))

# %%
def replace_hospital_city(hospitals, source, replacement):
    hospitals['city'] = hospitals['city'].replace(source, replacement)

replaces = {
    'anantapur': 'ananthapuramu',
    'anantpur': 'ananthapuramu',
    'allahabad': 'prayagraj',
    'aluva': 'ernakulam',
    'bahadurgarh': 'jhajjar',
    'bangalore': 'bangalore urban',
    'bengaluru rural': 'bangalore rural',
    'bantwal': 'dakshina kannada',
    'baramati': 'pune',
    'bardhaman': 'purba bardhaman',
    'behrampore': 'murshidabad',
    'belgaum': 'belagavi',
    'belguam': 'belagavi',
    'bellary': 'ballari',
    'berhampur': 'ganjam',
    'bhatinda': 'bathinda',
    'bhubaneswar': 'khurda',
    'bijnore': 'bijnor',
    'binaga': 'uttara kannada',
    'burdhwan': 'bardhaman',
    'calicut': 'kozhikode',
    'chamrajnagar': 'chamarajanagar',
    'chickmangalore': 'chikmagalur',
    'chikmagalaur': 'chikmagalur',
    'chikmaglur': 'chikmagalur',
    'chikkamagaluru': 'chikmagalur',
    'chitoor': 'chittoor',
    'cochin': 'ernakulam',
    'davangere': 'davanagere',
    'delhi': 'new delhi',
    'durgapur': 'paschim bardhaman',
    'gandhi nagar': 'gandhinagar',
    'ganganagar': 'sri ganganagar',
    'gautam buddha nagar': 'noida',
    'goa': 'north goa',
    'gokak': 'belagavi',
    'greater noida': 'gautam buddha nagar',
    'gulbarga': 'kalaburagi',
    'gurgaon': 'gurugram',
    'guwahati': 'kamrup metro',
    'hajipur': 'vaishali',
    'haldwani': 'nainital',
    'hanumangarh jn': 'hanumangarh',
    'himmatnagar': 'sabarkantha',
    'hoogli': 'hooghly',
    'hospet': 'vijayanagara',
    'hosur': 'krishnagiri',
    'hubli': 'dharwad',
    'jallandhar': 'jalandhar',
    'jalore city': 'jalore',
    'kadapa': 'ysr kadapa',
    'kalyan': 'thane',
    'kamothe': 'raigad',
    'kamrup metro': 'kamrup metropolitan',
    'kanpur': 'kanpur nagar',
    'karaikudi': 'sivaganga',
    'karwar': 'uttara kannada',
    'khanna': 'ludhiana',
    'khurda': 'khordha',
    'kochi': 'ernakulam',
    'kundapur': 'udupi',
    'kurushestra': 'kurukshetra',
    'madikeri': 'kodagu',
    'mallapuram': 'malappuram',
    'mangalore': 'dakshina kannada',
    'manjeri': 'malappuram',
    'marthandam': 'kanyakumari',
    'medinipur': 'paschim medinipur',
    'mohali': 'sahibzada ajit singh nagar',
    'mumbai': 'mumbai city',
    'muzffarpur': 'muzaffarpur',
    'mysuru': 'mysore',
    'nagercoil': 'kanyakumari',
    'nanjangud': 'mysuru',
    'nasik': 'nashik',
    'navi mumbai': 'thane',
    'nelamangala': 'bengaluru rural',
    'noida': 'gautam buddha nagar',
    'north 24 parganas': 'north 24 parganas',
    'ongole': 'prakasam',
    'ooty': 'nilgiris',
    'panaji': 'north goa',
    'pollachi': 'coimbatore',
    'pondicherry': 'puducherry',
    'proddutur': 'ysr kadapa',
    'purnea': 'purnia',
    'puttur': 'dakshina kannada',
    'rajahmundry': 'east godavari',
    'rajpura': 'patiala',
    'ramanagra': 'ramanagara',
    'ropar': 'rupnagar',
    'rudrapur': 'udham singh nagar',
    'secunderabad': 'hyderabad',
    'serampore': 'hooghly',
    'shivamogga': 'shimoga',
    'siliguri': 'darjeeling',
    'sirsi': 'uttara kannada',
    'sivakasi': 'virudhunagar',
    'sohna': 'gurugram',
    'sonepat': 'sonipat',
    'sriganganagar': 'sri ganganagar',
    'tadepalligudem': 'west godavari',
    'tanuku': 'west godavari',
    'thiruvananthapuram': 'thiruvananthapuram',
    'tirthahalli': 'shivamogga',
    'trichur': 'thrissur',
    'trichy': 'tiruchirappalli',
    'trivandrum': 'thiruvananthapuram',
    'tumkur': 'tumakuru',
    'tuticorin': 'thoothukudi',
    'udhamsinghnagar': 'udham singh nagar',
    'vapi': 'valsad',
    'vijayawada': 'krishna',
    'vijaywada': 'krishna',
    'wayanand': 'wayanad',
    'yamuna nagar': 'yamunanagar',
    'zirakapur': 'sahibzada ajit singh nagar'
}



for source, replacement in replaces.items():
    replace_hospital_city(hospitals, source, replacement)
for source, replacement in replaces.items():
    replace_hospital_city(hospitals, source, replacement)


# %%
hospitals = hospitals.merge(districts[['district', 'Density']], left_on='city', right_on='district', how='left')


# %%
hospitals['District'] = hospitals['district'].str.title()
hospitals.drop(columns=['city', 'district'], inplace=True)
hospitals = hospitals[['id', 'City', 'State', 'District', 'Density', 'Latitude', 'Longitude', 'Rating', 'Number of Reviews']]
hospitals.to_csv('../data/main/7-hospitals_population_densities.csv', index=False)


