from emdad import api, fields, models
from twilio.rest import Client
import requests

class EmdadContacts(models.Model):
    _name="emdad.contacts"

    name = fields.Char(string="Contact Name")
    contact_type = fields.Selection([('vendor','Vendor'), ('customer','Customer'), ('employee','Employee')], string="Contact Type")
    phone = fields.Char(string="Phone")
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


class EmdadCities(models.Model):
    _name = "emdad.cities"
    
    name = fields.Char(string="City Name")
    country = fields.Many2one("emdad.countries", string="Country")

class EmdadCountries(models.Model):
    _name = "emdad.countries"
    
    name = fields.Char(string="Country Name")
