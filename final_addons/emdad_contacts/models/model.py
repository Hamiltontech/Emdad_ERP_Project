from emdad import api, fields, models
from twilio.rest import Client
import requests
import re
from emdad.exceptions import ValidationError

class EmdadContacts(models.Model):
    _name="emdad.contacts"

    name = fields.Char(string="Contact Name", required=True)
    logo_image = fields.Binary(string="Logo")
    contact_type = fields.Selection([('vendor','Vendor'), ('customer','Customer'), ('employee','Employee')], string="Contact Type",required=True)
    phone = fields.Char(string="Phone",required=True)
    email = fields.Char(string="Official Email")
    website = fields.Char(string="Website")
    cr_number = fields.Char(string="CR Number", unique="True")
    vat_id = fields.Char(string="VAT ID")
    building = fields.Char(string="Building Number")
    street_name = fields.Char(string="Street Name")
    city = fields.Many2one("emdad.cities", string="City Name")
    district = fields.Char(string="District")
    related_company = fields.Many2one("res.company", string="Related Company")
    crEntityNumber = fields.Char(string="Entity Number")
    description = fields.Text(string="Business Description (English)")
    description_ar = fields.Text(string="Business Description (Arabic)")
    zip_code = fields.Char(string="Zip Code")
    from_wathq = fields.Boolean(string="From Wathiq")
    cr_copy = fields.Binary(string="CR Copy")
    account = fields.Selection([('verified','Verified'), ('not','Not Verified')], string="Status", default="not")
    selling_transactions = fields.Integer(compute='_compute_total_selling_transactions',string="Total selling transactions")
    procurement_transactions = fields.Integer(compute='_compute_total_procurement_transactions',string="Total procurement transactions")    
    selling_transactions = fields.Integer(compute='_compute_total_selling_transactions',string="Total selling transactions")
    procurement_transactions = fields.Integer(compute='_compute_total_procurement_transactions',string="Total procurement transactions")
    category = fields.Many2one("product.emdad.category", string="Related Category")
    def on_cr_number(self):
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
                self.name = cr_info.get('crName', '')
                self.crEntityNumber = cr_info.get('crEntityNumber', '')
                api_url_address = f'https://api.wathq.sa/v5/commercialregistration/address/{self.cr_number}'
                headers_address = {
                    'accept': 'application/json',
                    'apiKey': 'g36VC0YZOQR7kS4HgaH9X1WAX4rDgJlW'  # Replace with your API key
                }

                response_address = requests.get(api_url_address, headers=headers_address)

                if response_address.status_code == 200:
                    address_info = response_address.json().get('general', {})

                    self.website = address_info.get('website', '')
                    self.street_name = address_info.get('address', '')
                    self.email = address_info.get('email', '')
                    self.zip_code = address_info.get('zipcode', '')
                    self.phone = address_info.get('telephone1', '')
                    self.building = response_address.json().get('national', {}).get('unitNumber', '')
                    self.district = response_address.json().get('national', {}).get('districtName', '')
                    self.from_wathq = True
                    self.account = 'verified'
                else:
                    pass
            elif not self.cr_number:
                raise ValidationError('You need to input the CR Number to get the company information from Wathq')
            else: 
                pass
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
                self.name = cr_info.get('crName', '')
                self.crEntityNumber = cr_info.get('crEntityNumber', '')
                api_url_address = f'https://api.wathq.sa/v5/commercialregistration/address/{self.cr_number}'
                headers_address = {
                    'accept': 'application/json',
                    'apiKey': 'g36VC0YZOQR7kS4HgaH9X1WAX4rDgJlW'  # Replace with your API key
                }

                response_address = requests.get(api_url_address, headers=headers_address)

                if response_address.status_code == 200:
                    address_info = response_address.json().get('general', {})

                    self.website = address_info.get('website', '')
                    self.street_name = address_info.get('address', '')
                    self.email = address_info.get('email', '')
                    self.zip_code = address_info.get('zipcode', '')
                    self.phone = address_info.get('telephone1', '')
                    self.building = response_address.json().get('national', {}).get('unitNumber', '')
                    self.district = response_address.json().get('national', {}).get('districtName', '')
                    self.from_wathq = True
                    self.account = 'verified'
                else:
                    pass
            else:
                pass
    def send_sms_invite(self):
        account_sid = 'AC7f8f523885e4938a73936ce0f5b498d8'
        auth_token = '94c68fb4dcae33a87edd29107e3c3c4c'
        twilio_phone_number = '+18582603816'

        client = Client(account_sid, auth_token)

        contacts = self.search([])

        for contact in contacts:
            message_body = f"Dear {contact.name}, we would like to invite you to Emdad"
            print(f"Sending SMS to {contact.name} at phone number {contact.phone}")
            
            message = client.messages.create(
                body=message_body,
                from_=twilio_phone_number,
                to=contact.phone
            )

        return True
    
    @api.model
    def create(self, vals):
        if vals.get('email'):
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', vals.get('email'))
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

        if vals.get('phone'):
            match = re.match('\\+{0,1}[0-9]{10,12}', vals.get('phone'))
            if match == None:
                raise ValidationError('Invalid Phone Number')
        return super(EmdadContacts, self).create(vals)
    
    def _compute_total_selling_transactions(self):
        for record in self:
            sales_records = self.env['emdad.sales']
            subquery = sales_records.search([
                ('customer', '=', record.id)
            ])
            total_records = len(subquery.read())
            record.selling_transactions = total_records

    def _compute_total_procurement_transactions(self):
        for record in self:
            procurement_records = self.env['emdad.procurement']
            subquery = procurement_records.search([
                ('vendor', '=', record.id)
            ])
            total_records = len(subquery.read())
            record.procurement_transactions = total_records

class EmdadCities(models.Model):
    _name = "emdad.cities"
    
    name = fields.Char(string="City Name")
    country = fields.Many2one("emdad.countries", string="Country")

class EmdadCountries(models.Model):
    _name = "emdad.countries"
    
    name = fields.Char(string="Country Name")
