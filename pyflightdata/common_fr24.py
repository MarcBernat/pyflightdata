from .common import *
import sys

ROOT = 'http://www.flightradar24.com'
REG_BASE = 'https://api.flightradar24.com/common/v1/flight/list.json?query={0}&fetchBy=reg&page=1&limit=100&token={1}'
FLT_BASE = 'https://api.flightradar24.com/common/v1/flight/list.json?query={0}&fetchBy=flight&page=1&limit=100&token={1}'
AIRPORT_BASE = 'http://www.flightradar24.com/data/airports/{0}'
AIRLINE_BASE = 'https://www.flightradar24.com/data/aircraft/{0}'
AIRLINE_FLT_BASE = 'https://www.flightradar24.com/data/flights/{0}'
IMAGE_BASE = 'https://www.flightradar24.com/aircrafts/images/?aircraft={0}'
LOGIN_URL='https://www.flightradar24.com/user/login'

# Handle all the flights data


def get_raw_flight_data(url):
    data = get_raw_data_json(url, 'result.response.data')
    if data:
        return data[0] or []
    return []

def process_raw_flight_data(data, by_tail=False):
    #TODO check later if we need to parse this data - for now return full set
    return data


def get_data(url, by_tail=False):
    data = get_raw_flight_data(url)
    return process_raw_flight_data(data, by_tail)

# Handle getting countries


def get_raw_country_data():
    return get_raw_data(AIRPORT_BASE.format(''), 'tbl-datatable', 'tbody','tr') or []


def process_raw_country_data(data):
    result = []
    for entry in data:
        cells = entry.find_all('td')
        if cells:
	    record={}
            #this will break one day
            for cell in cells[1:2]:
                link = cell.find('a')
                if link:
                    if 'data-country' in link.attrs:
                        for attr in link.attrs:
                            if attr not in ['href','class','onclick','title']:
                                attr_new = attr.replace('data-','')
                                record[attr_new] = link[attr]
                        images = link.find_all('img')
                        if images:
                            for image in images:
                                try: 
                    			record['img'] = image['data-bn-lazy-src']
				except:
			    		pass
	    #also will break one day :D
	    for cell in cells[3:4]:
		 count = cell.find('span')
		 if count:
		    record['count'] = count.string.strip();
		 #prevents empty dictionary
	if record:
    	    result.append(record)
    return result


def get_countries_data():
    data = get_raw_country_data()
    return process_raw_country_data(data)

# Handle getting the airports in a country
def get_raw_airport_data(url):
    return get_raw_data(url, 'tbl-datatable', 'tbody','tr') or []


def process_raw_airport_data(data):
    result = []
    for entry in data:
        cells = entry.find_all('td')
        if cells:
            for cell in cells:
		extra = cell.find('small')
                link = cell.find('a')
		record={} 
                if link:
		    if extra:
			#Obtain ICAO from <small> tag
			for char in '()':
			    extra.string = extra.string.replace(char,'') 
			clean = extra.string.split("/")
			record['icao'] = clean[1]
                    if 'data-iata' in link.attrs:
                        for attr in link.attrs:
                            if attr not in ['href','class','onclick']:
                                attr_new = attr.replace('data-','')
                                if attr_new == 'title':
                                    attr_new = 'name'
                                record[attr_new] = link[attr]
                        result.append(record)
    return result


def get_airports_data(url):
    data = get_raw_airport_data(url)
    return process_raw_airport_data(data)

# handle aircraft information
def get_aircraft_data(url):
    info_data = get_raw_aircraft_info_data(url)
    images = get_raw_aircraft_image_data(url)
    return process_raw_aircraft_info_data(info_data, images)

def get_raw_aircraft_image_data(url):
    return get_raw_data_class_all(url, 'col-xs-6 n-p cnt-picture') or []


def get_raw_aircraft_info_data(url):
    return get_raw_data_class_all(url, 'row h-30 p-l-20 p-t-5') or []


def process_raw_aircraft_image_data(data):
    result = []
    for item in data:
        values = item.values()
        for entry in values:
            result.append(entry['src'])
    return result


def process_raw_aircraft_info_data(data, images):
    result = []
    record = {}
    for item in data:
        label = item.find('label')
        if label:
            key = encode_and_get(label.text.strip().lower())
            if '\\' in key:
                key = key[0:key.index('\\')]
            key = key.replace(' (msn)','')
            key = key.replace(' ','-')
            span = item.find('span')
            if span:
                value = encode_and_get(span.text.strip().lower())
                record[key] = value
    if images:
	img = []
	try:
		for image in images:
			span = image.find('a')
			i = span.findAll('img')[0].get('src')
			img.append(i)
		record['images'] = img	
	except:
		pass
    if len(record)>0:
        result.append(record)
    return result

# Handle getting all the airlines


def get_raw_airlines_data(url):
    return get_raw_data(url, 'tbl-datatable', 'tbody', 'tr') or []


def process_raw_airlines_data(data):
    result = []
    for entry in data:
        record = {}
        cells = entry.find_all('td')
        if cells:
            for cell in cells:
                link = cell.find('a')
                if link:
                    if 'data-country' in link.attrs:
                        for attr in link.attrs:
                            if attr not in ['href','class','onclick','target','data-country']:
                                attr_new = attr.replace('data-','')
                                record[attr_new] = link[attr]
                        href = link['href']
                        if href:
                            code = href.split('/')[-1:]
                            record['airline-code'] = code[0]
                        span = link.find('span')
                        if span:
                            images = span.find_all('img')
                            if images:
                                for image in images:
					try: 
                                    		record['img'] = image['data-bn-lazy-src']
					except:
				    		pass
                if 'class' in cell.attrs:
                    if 'text-right' in cell['class']:
                        value = encode_and_get(cell.text.strip())
                        if 'aircraft' in value:
                            record['fleet-size'] = value
                        else:
                            record['callsign'] = value
        if len(record)>0:
            result.append(record)
    return result


def get_airlines_data(url):
    data = get_raw_airlines_data(url)
    return process_raw_airlines_data(data)

# Handle getting the fleet


def get_raw_airline_fleet_data(url):
    slide =  get_raw_data_class(url, 'horizontal-slide')
    return slide.find_all('li',class_='parent') if slide else []

def process_raw_airline_fleet_data(data):
    result = []
    for parent in data:
        record = {}
        div = parent.find('div')
        if div:
            #yeah this sucks
            div = div.find('div')
            if div:
		#python split() http://www.pythonforbeginners.com/dictionary/python-split
		aircraft_type,count = div.text.split()
		record['aircraft-type'] = aircraft_type
		record['count'] = count
	img = parent.find('img')
	if img:
		try:
			record['img'] = img['src']
		except:
			pass
        ul = parent.find('ul')
        if ul:
            regs = ul.find_all('li')
            if regs:
                reg_list = []
                for reg in regs:
                    link = reg.find('a')
                    if link:
                        reg_list.append(encode_and_get(link.text.strip()))
                record['aircraft-regs'] = reg_list
        result.append(record)
    return result


def get_airline_fleet_data(url):
    data = get_raw_airline_fleet_data(url)
    return process_raw_airline_fleet_data(data)

# Handle getting the all the flights

def get_raw_airline_flight_data(url):
    return get_raw_data(url, 'tbl-datatable', 'tbody','tr') or []


def process_raw_airline_flight_data(data):
    result = []
    for entry in data:
        cells = entry.find_all('td')
        if cells:
            record = {}
            record['flight'] = encode_and_get(cells[1].text)
            record['from'] = cells[2]['title']
            record['to'] = cells[3]['title']
            link = cells[2].find('a')
            if link:
                record['from_iata'] = link.text
            link = cells[3].find('a')
            if link:
                record['to_iata'] = link.text
            record['aircraft-type'] = encode_and_get(cells[4].text)
            link = cells[5].find('a')
            if link:
                record['aircraft'] = encode_and_get(link.text)
            result.append(record)
    return result


def get_airline_flight_data(url):
    data = get_raw_airline_flight_data(url)
    return process_raw_airline_flight_data(data)
