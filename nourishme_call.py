import requests
import json
import logging

menu_url = "https://nourish.me/api/v1/menu"
bulk_order_url = "https://nourish.me/api/v1/bulk/order"

def get_menu_dishes():
	""" This function get menu items
	from nourish.me and then return a dictionary
	of name,id on success else it sends 400"""
		
	dishes_dict = {}
	try:
		
		headers = {'Content-type': 'application/json'}
		menu_api_resp = requests.get(menu_url,headers=headers)
		if menu_api_resp.status_code == 200: 
			menu_json = json.loads(menu_api_resp.content)
			for item in menu_json["dishes"]:	
				id = item["id"]
				name = item["name"]
				dishes_dict[name] = id
		else:	
			logging.error("FOOD_ORDER: Unable to fetch Menu. Reason: %s", menu_json.text)
			print("Unable to fetch Menu. Reason: ", menu_json.text)
			return 400
	except Exception as e:
		logging.error("FOOD_ORDER: Unable to fetch Menu. Reason: %s", str(e))
		print("Unable to fetch Menu. Reason: ", str(e))
		return 400
	
	return dishes_dict

def place_bulk_order(order_dict):
	""" This function will place 
	bulk order. It returns 200 on success 
	and 400 on Failure"""

	try:
		post_bulk_order = requests.post(bulk_order_url, data=order_dict)
		if post_bulk_order.status_code == 200:
			return 200
		else:
			logging.error("FOOD_ORDER: Not able to place bulk request. Reason: %s", post_bulk_order.text)
			print("Not able to place bulk request. Reason: ", post_bulk_order.text)
			return 400
	except Exception as e:
		logging.error("FOOD_ORDER: Not able to place bulk request. Reason: %s",str(e))
		print("Not able to place bulk request. Reason: ", str(e))
		return 400
	
