import json

with open('robi-roaming.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

call_rates = {country['title_en']: country['call_rate'] for country in data['countriesCallRates']['items']}


with open('output.txt', 'w', encoding='utf-8') as f:
    for country in data['countries']['items']:
        country_name = country['title_en']
        f.write(f"Country: {country_name}\n")
        print(f"Country: {country_name}\n")
        
     
        if country_name in call_rates:
            call_rate = call_rates[country_name]
            f.write(f"    Mobile Rate: {call_rate['mobile_rate_en']}\n")
            f.write(f"    Land Rate: {call_rate['land_rate_en']}\n")
            print(f"    Mobile Rate: {call_rate['mobile_rate_en']}\n")
            print(f"    Land Rate: {call_rate['land_rate_en']}\n")
        else:
            f.write("    Call Rates: Not Available\n")
            print("    Call Rates: Not Available\n")
        
  
        if country.get('service_prepaid'):  
            for service in country['service_prepaid']:
                f.write(f"        Prepaid Service: {service['service_en']} - {service['value_en']}\n")
                print(f"        Prepaid Service: {service['service_en']} - {service['value_en']}\n")
        else:
            f.write("    Prepaid: Not Available\n")
            print("    Prepaid: Not Available\n")
            

       
        if country.get('service_postpaid'):  
            for service in country['service_postpaid']:
                f.write(f"    Postpaid Service: {service['service_en']} - {service['value_en']}\n")
                print(f"    Postpaid Service: {service['service_en']} - {service['value_en']}\n")
        else:
            f.write("    Postpaid: Not Available\n")
            print("    Postpaid: Not Available\n")
        

        f.write("\n")
        print("\n")
        
