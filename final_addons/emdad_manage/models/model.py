from emdad import fields, models, api
from datetime import datetime
import requests
from twilio.rest import Client

class EmdadCustomer(models.Model):
    _name="emdad.customer"

    name = fields.Char(string="Customer ID")
    contact_name = fields.Char(string="Contact Name", compute="_make_name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Second Name")
    last_name = fields.Char(string="Last Name")
    status = fields.Selection([('new','New'),('active','In Progress'), ('expired','Expired')], string="Status", compute="_calculate_status")
    start_date = fields.Date(string="Start Date")
    next_renewal = fields.Date(string="Next Renewal")
    period = fields.Float(string="Subscription Months", compute="_calculate_months")
    days_until_renewal = fields.Float(string="Remaining Days", compute="_calculate_days_until_renewal")
    #server_information
    plan = fields.Selection([('nano','Emdad Nano'),('micro','Emdad Micro'),('custom','Emdad Pro')], string="Assigned Plan")
    ip_address = fields.Char(string="IP Address")
    domain_name = fields.Char(string="Domain Name")
    #company
    company = fields.Char(string="Company Name")
    cr_number = fields.Char(string="Company CR")
    street_name = fields.Char(string="Street")
    zip_code = fields.Char(string="ZIP Code")
    phone = fields.Char(string="Phone Number")
    district = fields.Char(string="District")
    building = fields.Char(string="Building")
    description_ar = fields.Char(string="Description Arabic")
    description = fields.Char(String="Description")
    email = fields.Char(string="Company Email")
    crEntityNumber = fields.Char(string="Entity Number")
    city = fields.Many2one("res.country.state", string="City")
    country = fields.Many2one("res.country", string="Country")
    emdad_market = fields.Boolean(string="Has Emdad Market")
    server_action = fields.Selection([('running','Running'), ('restarting','Restarting'), ('down','Down')], string="Server Action", default="running")

    def shut_down_server(self):
        for record in self:
            record.server_action = 'down'
    def restart_server(self):
        for record in self:
            record.server_action = 'restarting'
    @api.onchange('cr_number')
    def on_change_cr_number(self):
        if self.cr_number:
            api_url = f'https://api.wathq.sa/v5/commercialregistration/info/{self.cr_number}'
            headers = {
                'accept': 'application/json',
                'apiKey': 'g36VC0YZOQR7kS4HgaH9X1WAX4rDgJlW'  # Replace with your API key
            }

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                cr_info = response.json()
                isic_list = cr_info.get('activities', {}).get('isic', [])
                if isic_list:
                    isic_info = isic_list[0]
                    self.description_ar = isic_info.get('name', '')
                    self.description = isic_info.get('nameEN', '')
                self.company = cr_info.get('crName', '')
                self.crEntityNumber = cr_info.get('crEntityNumber', '')
                api_url_address = f'https://api.wathq.sa/v5/commercialregistration/address/{self.cr_number}'
                headers_address = {
                    'accept': 'application/json',
                    'apiKey': 'g36VC0YZOQR7kS4HgaH9X1WAX4rDgJlW'  # Replace with your API key
                }

                response_address = requests.get(api_url_address, headers=headers_address)

                if response_address.status_code == 200:
                    address_info = response_address.json().get('general', {})

                    self.domain_name = address_info.get('website', '')
                    self.street_name = address_info.get('address', '')
                    self.email = address_info.get('email', '')
                    self.zip_code = address_info.get('zipcode', '')
                    self.phone = address_info.get('telephone1', '')
                    self.building = response_address.json().get('national', {}).get('unitNumber', '')
                    self.district = response_address.json().get('national', {}).get('districtName', '')
                  
                else:
                    pass
            else:
                pass
    @api.depends('first_name', 'middle_name', 'last_name')
    def _make_name(self):
        for record in self:
            if record.first_name and record.middle_name and record.last_name:
                record.contact_name = record.first_name + ' ' + record.middle_name + ' ' + record.last_name
            else:
                record.contact_name = 'Contact Name Not Defined'
    
    @api.depends('start_date', 'next_renewal')
    def _calculate_months(self):
        for record in self:
            if record.start_date and record.next_renewal:
                start_date = fields.Date.from_string(record.start_date)
                next_renewal = fields.Date.from_string(record.next_renewal)
                delta = next_renewal - start_date
                record.period = delta.days / 30.44  
            else:
                record.period = 0.0

    @api.depends('next_renewal')    
    def _calculate_status(self):
        for record in self:
            if record.next_renewal:
                current_date = datetime.now().date()
                next_renewal = fields.Date.from_string(record.next_renewal)
                if current_date < next_renewal:
                    record.status = 'active'
                else:
                    record.status = 'expired'
            else:
                record.status = 'new'

    @api.depends('next_renewal')
    def _calculate_days_until_renewal(self):
        for record in self:
            if record.next_renewal:
                today = datetime.now().date()
                remaining_days = (record.next_renewal - today).days
                record.days_until_renewal = remaining_days

                # Check if 10 days remaining or subscription expired
                if remaining_days == 10:
                    record.send_twilio_message("Your subscription will expire in 10 days.")
                elif remaining_days < 0:
                    record.send_twilio_message("Your subscription has expired.")

    def send_twilio_message(self, message):
        # Your Twilio Account SID, Auth Token, and Twilio phone number
        account_sid = "AC7f8f523885e4938a73936ce0f5b498d8"
        auth_token = "94c68fb4dcae33a87edd29107e3c3c4c"
        twilio_phone_number = "+18582603816"

        to_phone_number = self.phone

        client = Client(account_sid, auth_token)

        # Send SMS using Twilio
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_phone_number
        )