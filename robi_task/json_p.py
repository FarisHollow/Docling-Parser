import requests
import json
from bs4 import BeautifulSoup

# URL to scrape
url = "https://www.bd.airtel.com/en/personal/roaming/roaming-home"


response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

script_t = soup.find(id="__NEXT_DATA__")

cleaned_script = str(script_t).replace("\\n", "").replace(
    '<script id="__NEXT_DATA__" type="application/json">', "").replace("</script>", "")
scrap_data = json.loads(cleaned_script)



def extract_roaming_bundles(data):
    if isinstance(data, dict):
        if 'roamingBundles' in data:
            for item in data['roamingBundles']:
                print("Roaming Bundle:")
                print(f"  Title (English): {item.get('title_en')}")
                print(f"  Price: {item.get('price')} {item.get('price_type')}")
                print(f"  Duration: {item.get('duration')} hours")
                print(f"  Short Description: {item.get('short_description_en')}")

        else:
            for key, value in data.items():
                extract_roaming_bundles(value)
                
                



def extract_countries(data):
    if isinstance(data, dict):
        if 'countries' in data:
            for country in data['countries']['items']:
                country_name = country.get('title_en')
                print(f"Country: {country_name}")

                with open('country.txt', 'a', encoding='utf-8') as f:
                    f.write(f"Country: {country_name}\n")
                    print(f"Country: {country_name}")

                    if 'service_prepaid' in country and country['service_prepaid']:
                        f.write("    Prepaid Service:\n")
                        print("    Prepaid Service:")
                        for service in country['service_prepaid']:
                            service_en = service.get('service_en', 'N/A')
                            value_en = service.get('value_en', 'N/A')
                            f.write(f"    -> {service_en} - {value_en}\n")
                            print(f"    -> {service_en} - {value_en}")
                    else:
                        f.write("    Prepaid Service: Not Available\n")
                        print("    Prepaid Service: Not Available")
                    
                    f.write("\n")
                    print("\n")

                    if 'service_postpaid' in country and country['service_postpaid']:
                        f.write("    Postpaid Service:\n")
                        print("    Postpaid Service:")
                        for service in country['service_postpaid']:
                            service_en = service.get('service_en', 'N/A')
                            value_en = service.get('value_en', 'N/A')
                            f.write(f"    -> {service_en} - {value_en}\n")
                            print(f"    -> {service_en} - {value_en}")
                    else:
                        f.write("    Postpaid Service: Not Available\n")
                        print("    Postpaid Service: Not Available")

                    f.write("\n")
                    print("\n")


        else:
            for key, value in data.items():
                extract_countries(value)



                


def extract_offers(data):
    if isinstance(data, dict):
     
        if 'offers' in data:
              for offer in data['offers']['items']:
                offer_title = offer.get('title_en')
                offer_price = offer.get('price')
                offer_price_type = offer.get('price_type')
                offer_duration = offer.get('duration')
                offer_description = offer.get('short_description_en')
                
                print(f"Offer Title: {offer_title}")
                print(f"Price: {offer_price}")
                print(f"Price Type: {offer_price_type}")
                print(f"Duration: {offer_duration} hours")
                print(f"Description: {offer_description}")

                with open('offers.txt', 'a', encoding='utf-8') as f:
                    f.write(f"Offer Title: {offer_title}\n")
                    f.write(f"Price: {offer_price}\n")
                    f.write(f"Price Type: {offer_price_type}\n")
                    f.write(f"Duration: {offer_duration} hours\n")
                    f.write(f"Description: {offer_description}\n\n")


def extract_need_to_know(data):
    if isinstance(data, dict):
        if 'needToKnow' in data:           
            for item in data['needToKnow']['items']:
                title = item.get('title_en')
                if title:
                    print(f"Title: {title}")
                else:
                    print("Title not available")






# entries
extract_countries(scrap_data)
# extract_roaming_bundles(scrap_data)
# extract_offers(scrap_data)
# extract_need_to_know(scrap_data)

                 
