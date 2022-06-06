from xml.dom import minidom
import requests
import json
import sys
import nourishme_call
import logging
import os.path

logging.basicConfig(filename="orderfood.log", level=logging.DEBUG,\
	format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
def convert_inputxml_to_json(employee_orders_file):
	try:
		if not os.path.exists(employee_orders_file):
			print("File not present at path : ", employee_orders_file)
			logging.error("FOOD_ORDER: File not present at path : %s", employee_orders_file) 
			return 400

		order_file_content = minidom.parse(employee_orders_file)
		employee_details = order_file_content.getElementsByTagName("Employee")
		order_dict={}
		order_dict["orders"] = []	
	
		# create dictionary of menu items
		dishes_dict = nourishme_call.get_menu_dishes()
		logging.debug("FOOD_ORDER: The dishes dict is: %s", dishes_dict)
		if dishes_dict == 400:
			logging.error("FOOD_ORDER: Error fetching Menu items")
			print("Error fetching Menu items")
			return 400
		
		#create final json to send at food website for bulk order
		for employee in employee_details:
			isAttending=employee.getElementsByTagName("IsAttending")[0].childNodes[0].data
			if isAttending == "true":
				emp_name = employee.getElementsByTagName("Name")[0].childNodes[0].data
				logging.info("FOOD_ORDER: %s employee will attend the event", emp_name)
				emp_address = employee.getElementsByTagName("Address")
				emp_street = emp_address[0].getElementsByTagName("Street")[0].childNodes[0].data
				emp_city = emp_address[0].getElementsByTagName("City")[0].childNodes[0].data
				emp_postal = emp_address[0].getElementsByTagName("PostalCode")[0].childNodes[0].data
				emp_order = employee.getElementsByTagName("Order")[0].childNodes[0].data
	
				customer_dict = {}
				customer_dict["customer"] = {}
				customer_dict["customer"]["name"] = emp_name
				address_dict = {}
				address_dict["street"] = emp_street
				address_dict["city"] = emp_city
				address_dict["postal_code"] = emp_postal
				customer_dict["customer"]["address"] = address_dict
			
				items_json = []
				order_items = emp_order.split(",")
				for item in order_items:
					amount = item.split("x")[0].strip()
					dish = item.split("x")[1].strip()
					items_dict = {}
					items_dict["id"] = dishes_dict[dish]
					items_dict["amount"] = int(amount)
					items_json.append(items_dict)
							
				customer_dict["items"] = items_json
				order_dict["orders"].append(customer_dict)
			else:
				emp_name = employee.getElementsByTagName("Name")[0].childNodes[0].data
				logging.info("FOOD_ORDER: %s employee will not attend the event", emp_name)
	
		request_json = json.dumps(order_dict)
		return request_json
	except Exception as e:
		logging.error("FOOD_ORDER: Exception occured parsing and converting xml file %s", str(e))
		print("Exception occured parsing and converting xml file", str(e))
		return 400

if len(sys.argv) != 2:
	print("input agument to the client is wrong")
	print("Please provide order xml file as first argument")
else:
	bulk_json = convert_inputxml_to_json(sys.argv[1])
	logging.info("FOOD_ORDER: bulk final json is - %s ", bulk_json) 
	if bulk_json != 400:
		post_bulk_json = nourishme_call.place_bulk_order(bulk_json)
		if post_bulk_json != 400:
			logging.info("FOOD_ORDER: bulk order processed successfully")
			print("bulk order processed successfully")
		else:
			logging.info("FOOD_ORDER: bulk order failed to process")
			print("bulk order failed to process") 
	else:
		logging.error("FOOD_ORDER: bulk order failed to process")
		print("bulk order failed to process")
