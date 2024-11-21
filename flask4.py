from flask import Flask, request, jsonify
import sounddevice as sd
import numpy as np
import wave
import google.generativeai as genai
import mysql.connector
import json
import time

app = Flask(__name__)

# Configure Google Generative AI
genai.configure(api_key="AIzaSyD61OB-gICJFTPh98DfpFYXVVOe76dk4yk")

# Function to record audio
def record_audio(filename, duration=13, samplerate=16000):
    print("Recording audio...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    print(f"Audio saved to {filename}")
    

# Function to transcribe audio
def transcribe_audio():
    myfile = genai.upload_file("recorded_audio.wav")
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = """Give an exact transcript of the speech in English and nothing else. 
                Also transcribe any number in the speech as a number only and not the spelling of the number.
             Make sure to translate each and every word carefully if speech is not in english."""
    result = model.generate_content([myfile, prompt])
    return result.text

# Use Gemini API to extract customer details from transcription
def extract_customer_details(transcription):
    prompt = f"""
    Here is a voice transcription: "{transcription}"
    Identify the customer's name, email, and contact number, and return only this JSON format:
    {{
      "customer_name": "Customer's name",
      "email": "Customer's email",
      "contact_number": "Customer's contact number"
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        json_start = response.text.find("{")
        json_end = response.text.rfind("}") + 1
        json_text = response.text[json_start:json_end]
        customer_data = json.loads(json_text)
        return customer_data
    except json.JSONDecodeError:
        return None

def extract_customer_id(transcription):
    prompt = f"""
    Here is a voice transcription: "{transcription}"
    Identify the customer ID which is an integer only and return only this JSON format:
    {{
      "customer_id": "Customer's ID only as an integer",
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        json_start = response.text.find("{")
        json_end = response.text.rfind("}") + 1
        json_text = response.text[json_start:json_end]
        customer_data = json.loads(json_text)
        return customer_data
    except json.JSONDecodeError:
        return None


def extract_employee_details(transcription):
    prompt = f"""
    Here is a voice transcription: "{transcription}"
    Identify the employees name, email, contact number, position/designation and address, and return only this JSON format:
    {{
      "employee_name": "Employee's name",
      "email": "Employee's email",
      "contact_number": "Employee's contact number"
      "position": "Employee's postion"
      "address": "Employee's address"
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        json_start = response.text.find("{")
        json_end = response.text.rfind("}") + 1
        json_text = response.text[json_start:json_end]
        emp_data = json.loads(json_text)
        return emp_data
    except json.JSONDecodeError:
        return None

def extract_inventoryItem_details(transcription):
    prompt = f"""
    Here is a voice transcription: "{transcription}"
    Identify the item name, quantity, unit, when it was last updated and supplier id, and return only this JSON format:
    {{
      "item_name": "Item name",
      "quantity": "quantity of the item (integer)",
      "unit": "unit of the items quantity given"
      "last_updated": "the current timestamp in the format of NOW() variable type in MySQL"
      "supplier_id": "Supplier id of who supplied the item"
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        json_start = response.text.find("{")
        json_end = response.text.rfind("}") + 1
        json_text = response.text[json_start:json_end]
        emp_data = json.loads(json_text)
        return emp_data
    except json.JSONDecodeError:
        return None


#need to fix
def extract_sale_details(transcription):
    prompt = f"""
    Here is a voice transcription: "{transcription}"
    Identify the sale date, total amount of the sale, payment method, customer ID and employee ID, and return only this JSON format:
    {{
      "sale_date": "Date of the sale (in 'date' format supported by mysql.)",
      "total_amount": "Total amount of the sale (Only amount, not currency)",
      "payment_method": "The payment method (one word)",
      "customer_id": "Customer ID (only a number in integer format)",
      "employee_id": "Employee ID (only a number in integer format)"
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        # Parse the JSON content
        json_start = response.text.find("{")
        json_end = response.text.rfind("}") + 1
        json_text = response.text[json_start:json_end]
        sale_data = json.loads(json_text)
        
        # Validate the extracted fields
        if not sale_data.get("sale_date") or not sale_data.get("total_amount") or \
           not sale_data.get("payment_method") or not sale_data.get("customer_id") or \
           not sale_data.get("employee_id"):
            raise ValueError("Missing essential sale details")

        # Return the correctly formatted sale data
        return sale_data
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error extracting sale details: {str(e)}")
        return None


def extract_supplier_details(transcription):
    prompt = f"""
    Here is a voice transcription: "{transcription}"
    Identify the suppliers name, email, contact number, and address, and return only this JSON format:
    {{
      "supplier_name": "Supplier's name",
      "email": "Supplier's email",
      "contact_number": "Supplier's contact number"
      "address": "Supplier's address"
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        json_start = response.text.find("{")
        json_end = response.text.rfind("}") + 1
        json_text = response.text[json_start:json_end]
        emp_data = json.loads(json_text)
        return emp_data
    except json.JSONDecodeError:
        return None

# Function to update a customer's details
def update_customer(customer_id, data):
    query = ("UPDATE Customers SET customer_name=%s, contact_number=%s, email=%s "
             "WHERE customer_id=%s")
    values = (data['customer_name'], data['contact_number'], data['email'], customer_id)

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Customer not found.'}), 404
            return jsonify({'message': 'Customer updated successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def update_employee(employee_id,data):
    query = ("UPDATE Employee SET employee_name=%s, position=%s, contact_number=%s, email=%s, address=%s "
             "WHERE employee_id=%s")
    values = (data['employee_name'], data['position'], data['contact_number'], data['email'], data['address'], employee_id)

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Employee not found.'}), 404
            return jsonify({'message': 'Employee updated successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def update_supplier(supplier_id,data):
    query = ("UPDATE Supplier SET supplier_name=%s, address=%s, email=%s, contact_number=%s "
             "WHERE supplier_id=%s")
    values = (data['supplier_name'], data['address'], data['email'], data['contact_number'], supplier_id)

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Supplier not found.'}), 404
            return jsonify({'message': 'Supplier updated successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def update_inventory_item(inventory_id,data):
    query = ("UPDATE Inventory SET item_name=%s, quantity=%s, unit=%s, last_updated=NOW(), supplier_id=%s "
             "WHERE inventory_id=%s")
    values = (data['item_name'], data['quantity'], data['unit'], data.get('supplier_id'), inventory_id)

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Inventory item not found.'}), 404
            return jsonify({'message': 'Inventory item updated successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="shs82199",
        database="restaurant"
    )

# Helper function to handle database errors
def handle_db_error(err):
    return jsonify({'error': True, 'message': str(err)}), 500

# Function to add a customer to the database
def add_customer(data):
    query = ("INSERT INTO customers (customer_name, contact_number, email) "
             "VALUES (%s, %s, %s)")
    values = (data['customer_name'], data['contact_number'], data['email'])
    
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            return jsonify({'message': 'Customer added successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def add_employee(data):
    query = ("INSERT INTO Employee (employee_name, position, contact_number, email, address) "
             "VALUES (%s, %s, %s, %s, %s)")
    values = (data['employee_name'], data['position'], data['contact_number'], data['email'], data['address'])

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            return jsonify({'message': 'Employee added successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def add_supplier(data):
    query = ("INSERT INTO Supplier (supplier_name, address, email, contact_number) "
             "VALUES (%s, %s, %s, %s)")
    values = (data['supplier_name'], data['address'], data['email'], data['contact_number'])

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            return jsonify({'message': 'Supplier added successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def add_inventory_item(data):
    query = ("INSERT INTO Inventory (item_name, quantity, unit, last_updated, supplier_id) "
             "VALUES (%s, %s, %s, NOW(), %s)")
    values = (data['item_name'], data['quantity'], data['unit'], data.get('supplier_id'))

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            return jsonify({'message': 'Inventory item added successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def add_sale(data):
    query = ("INSERT INTO Sales (sale_date, total_amount, payment_method, customer_id, employee_id) "
             "VALUES (%s, %s, %s, %s, %s)")
    values = (data['sale_date'], data['total_amount'], data['payment_method'],
              data.get('customer_id'), data.get('employee_id'))

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, values)
            cnx.commit()
            return jsonify({'message': 'Sale recorded successfully.'}), 200
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500


# Function to get all customers from the database
def get_customers():
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            return jsonify(customers), 200
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def get_employees():
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Employee")
            employees = cursor.fetchall()
            return jsonify(employees), 200
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def get_suppliers():
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Supplier")
            suppliers = cursor.fetchall()
            return jsonify(suppliers), 200
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def get_inventory_items():
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Inventory")
            items = cursor.fetchall()
            return jsonify(items), 200
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500


# Function to get a specific customer by customer_id
def get_customer(customer_id):
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
            customer = cursor.fetchone()
            if customer:
                return jsonify(customer), 200
            else:
                return jsonify({'message': 'Customer not found.'}), 404
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def get_employee(employee_id):
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Employee WHERE employee_id = %s", (employee_id,))
            employee = cursor.fetchone()
            if employee:
                return jsonify(employee), 200
            else:
                return jsonify({'message': 'Employee not found.'}), 404
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500
    
def get_supplier(supplier_id):
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Supplier WHERE supplier_id = %s", (supplier_id,))
            supplier = cursor.fetchone()
            if supplier:
                return jsonify(supplier), 200
            else:
                return jsonify({'message': 'Supplier not found.'}), 404
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def get_inventory_item(inventory_id):
    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Inventory WHERE inventory_id = %s", (inventory_id,))
            item = cursor.fetchone()
            if item:
                return jsonify(item), 200
            else:
                return jsonify({'message': 'Inventory item not found.'}), 404
        except mysql.connector.Error as err:
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500


def delete_customer(customer_id):
    query = "DELETE FROM Customers WHERE customer_id=%s"

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, (customer_id,))
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Customer not found.'}), 404
            return jsonify({'message': 'Customer deleted successfully.'}), 200
        except mysql.connector.IntegrityError:
            cnx.rollback()
            return handle_db_error("Cannot delete customer due to existing references in sales or reservations.")
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def delete_employee(employee_id):
    query = "DELETE FROM Employee WHERE employee_id=%s"

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, (employee_id,))
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Employee not found.'}), 404
            return jsonify({'message': 'Employee deleted successfully.'}), 200
        except mysql.connector.IntegrityError:
            cnx.rollback()
            return handle_db_error("Cannot delete employee due to existing references in orders, sales, or reservations.")
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def delete_supplier(supplier_id):
    query = "DELETE FROM Supplier WHERE supplier_id=%s"

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, (supplier_id,))
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Supplier not found.'}), 404
            return jsonify({'message': 'Supplier deleted successfully.'}), 200
        except mysql.connector.IntegrityError:
            cnx.rollback()
            return handle_db_error("Cannot delete supplier due to existing references in inventory.")
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

def delete_inventory_item(inventory_id):
    query = "DELETE FROM Inventory WHERE inventory_id=%s"

    cnx = get_db_connection()
    if cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query, (inventory_id,))
            cnx.commit()
            if cursor.rowcount == 0:
                return jsonify({'message': 'Inventory item not found.'}), 404
            return jsonify({'message': 'Inventory item deleted successfully.'}), 200
        except mysql.connector.IntegrityError:
            cnx.rollback()
            return handle_db_error("Cannot delete inventory item due to existing references in order items or menu.")
        except mysql.connector.Error as err:
            cnx.rollback()
            return handle_db_error(err)
        finally:
            cursor.close()
            cnx.close()
    else:
        return jsonify({'error': True, 'message': 'Database connection failed.'}), 500

    

# Route to record and process audio, then return transcription
@app.route('/transcribe_and_process_audio', methods=['POST'])
def transcribe_and_process_audio():
    # Record and save audio to file
    record_audio("recorded_audio.wav")
    
    # Transcribe audio
    transcription = transcribe_audio()
    
    # Return transcription as response
    return jsonify({"transcription": transcription}), 200

# Main route to process the voice command
@app.route('/process_command', methods=['POST'])
def process_command():
    transcription = request.json.get('transcription', '')
    if not transcription:
        return jsonify({'error': True, 'message': 'No transcription provided.'}), 400
    
    print(f"Received transcription: {transcription}")  # Added logging for debugging
    
    # Check for keywords in transcription to determine action
    if ("add" in transcription.lower() or "new" in transcription.lower()) and "customer" in transcription.lower():
        customer_data = extract_customer_details(transcription)
        if customer_data:
            return add_customer(customer_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract customer details from transcription.'}), 400
    elif "update" in transcription.lower() and "customer" in transcription.lower():
        # Extract customer details from transcription and update
        data1 = extract_customer_id(transcription)
        customer_id = data1['customer_id']
        customer_data = extract_customer_details(transcription)
        
        # if "ID" in transcription:
        #     try:
        #         customer_id = int(transcription.split("ID", 1)[1].strip())
        #     except ValueError:
        #         return jsonify({'error': True, 'message': 'Invalid customer ID.'}), 400
        
        if customer_id and customer_data:
            return update_customer(customer_id, customer_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract customer ID or details for update.'}), 400
    elif "show" in transcription.lower() and "all" in transcription.lower() and "customer" in transcription.lower():
        return get_customers()
    elif "show" in transcription.lower() and "customer" in transcription.lower():
        customer_id = transcription.split("ID")[-1].strip() if "ID" in transcription else None
        if customer_id:
            return get_customer(customer_id)
        else:
            return jsonify({'error': True, 'message': 'Customer ID not provided in transcription.'}), 400
    elif ("delete" in transcription.lower() or "remove") and "customer" in transcription.lower():
        data1 = extract_customer_id(transcription)
        customer_id = data1['customer_id']
        # if "ID" in transcription:
        #     try:
        #         customer_id = int(transcription.split("ID")[-1].strip())
        #     except ValueError:
        #         return jsonify({'error': True, 'message': 'Invalid customer ID.'}), 400
        
        if customer_id:
            return delete_customer(customer_id)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract customer ID for deletion.'}), 400

    elif ("add" in transcription.lower() or "new" in transcription.lower()) and "employee" in transcription.lower():
        emp_data = extract_employee_details(transcription)
        if emp_data:
            return add_employee(emp_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract employee details from transcription.'}), 400
    elif "show" in transcription.lower() and "all" in transcription.lower() and "employee" in transcription.lower():
        return get_employees()
    elif "show" in transcription.lower() and "employee" in transcription.lower():
        emp_id = transcription.split("ID")[-1].strip() if "ID" in transcription else None
        if emp_id:
            return get_employee(emp_id)
        else:
            return jsonify({'error': True, 'message': 'employee ID not provided in transcription.'}), 400
    elif "update" in transcription.lower() and "employee" in transcription.lower():
        # Extract customer details from transcription and update
        emp_id = None
        emp_data = extract_employee_details(transcription)
        
        if "ID" in transcription:
            try:
                emp_id = transcription.split("ID", 1)[1].strip()
                print(emp_id)
            except ValueError:
                print(emp_id)
                return jsonify({'error': True, 'message': 'Invalid employee ID.'}), 400
        if emp_id and emp_data:
            return update_employee(emp_id, emp_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract employee ID or details for update.'}), 400
    elif ("delete" in transcription.lower() or "remove") and "employee" in transcription.lower():
        emp_id = None
        if "ID" in transcription:
            try:
                emp_id = int(transcription.split("ID")[-1].strip())
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid employee ID.'}), 400
        if emp_id:
            return delete_employee(emp_id)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract employee ID for deletion.'}), 400

    elif ("add" in transcription.lower() or "new" in transcription.lower()) and "supplier" in transcription.lower():
        sup_data = extract_supplier_details(transcription)
        if sup_data:
            return add_supplier(sup_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract supplier details from transcription.'}), 400
    elif "show" in transcription.lower() and "all" in transcription.lower() and "supplier" in transcription.lower():
        return get_suppliers()
    elif "show" in transcription.lower() and "supplier" in transcription.lower():
        sup_id = transcription.split("ID")[-1].strip() if "ID" in transcription else None
        if sup_id:
            return get_supplier(sup_id)
        else:
            return jsonify({'error': True, 'message': 'supplier ID not provided in transcription.'}), 400
    elif "update" in transcription.lower() and "supplier" in transcription.lower():
        # Extract customer details from transcription and update
        sup_id = None
        sup_data = extract_supplier_details(transcription)
        
        if "ID" in transcription:
            try:
                sup_id = int(transcription.split("ID")[-1].strip())
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid supplier ID.'}), 400
        if sup_id and sup_data:
            return update_supplier(sup_id, sup_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract supplier ID or details for update.'}), 400
    elif ("delete" in transcription.lower() or "remove") and "supplier" in transcription.lower():
        sup_id = None
        if "ID" in transcription:
            try:
                sup_id = int(transcription.split("ID")[-1].strip())
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid supplier ID.'}), 400
        if sup_id:
            return delete_supplier(sup_id)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract supplier ID for deletion.'}), 400
            

    elif ("add" in transcription.lower() or "new" in transcription.lower()) and "inventory" in transcription.lower():
        item_data = extract_inventoryItem_details(transcription)
        if item_data:
            return add_inventory_item(sup_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract inventory item details from transcription.'}), 400
    elif "show" in transcription.lower() and "all" in transcription.lower() and "inventory" in transcription.lower():
        return get_inventory_items()
    elif "show" in transcription.lower() and "inventory" in transcription.lower():
        item_id = transcription.split("ID")[-1].strip() if "ID" in transcription else None
        if item_id:
            return get_inventory_item(item_id)
        else:
            return jsonify({'error': True, 'message': 'item ID not provided in transcription.'}), 400
    elif "update" in transcription.lower() and "inventory" in transcription.lower():
        item_id = None
        item_data = extract_inventoryItem_details(transcription)
        
        if "ID" in transcription:
            try:
                sup_id = int(transcription.split("ID")[-1].strip())
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid item ID.'}), 400
        if item_id and item_data:
            return update_inventory_item(item_id, item_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract item ID or details for update.'}), 400
    elif ("delete" in transcription.lower() or "remove") and "inventory" in transcription.lower():
        item_id = None
        if "ID" in transcription:
            try:
                item_id = int(transcription.split("ID")[-1].strip())
            except ValueError:
                return jsonify({'error': True, 'message': 'Invalid item ID.'}), 400
        if sup_id:
            return delete_inventory_item(item_id)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract item ID for deletion.'}), 400

    elif ("add" in transcription.lower() or "new" in transcription.lower()) and "sale" in transcription.lower():
        print("executing fn to add new sale")
        sale_data = extract_sale_details(transcription)
        print(sale_data)
        if sale_data:
            return add_sale(sale_data)
        else:
            return jsonify({'error': True, 'message': 'Unable to extract sale details from transcription.'}), 400
    else:
        return jsonify({'error': True, 'message': 'Unrecognized command in transcription.'}), 400

    

if __name__ == '__main__':
    app.run(debug=True)


#UPDATES TO BE MADE:
"""
need to fix inventory item search (search by item name)
(also update inventory items by item name)
"""
