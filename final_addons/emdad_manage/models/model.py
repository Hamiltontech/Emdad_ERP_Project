from emdad import fields, models, api
from datetime import datetime
import requests
from twilio.rest import Client
import boto3

class EmdadCustomer(models.Model):
    _name="emdad.customer"

    name = fields.Char(string="Customer ID", compute="_compute_subscription_id")
    update = fields.Char(string="Updates")
    contact_name = fields.Char(string="Contact Name", compute="_make_name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Second Name")
    last_name = fields.Char(string="Last Name")
    status = fields.Selection([('new','New'),('active','In Progress'), ('expired','Expired')], string="Status", compute="_calculate_status")
    start_date = fields.Date(string="Start Date")
    next_renewal = fields.Date(string="Next Renewal")
    period = fields.Float(string="Remaining Months", compute="_calculate_months")
    days_until_renewal = fields.Float(string="Remaining Days", compute="_calculate_days_until_renewal")
    plan = fields.Selection([('nano','Emdad Nano'),('micro','Emdad Micro'),('custom','Emdad Pro')], string="Assigned Plan")
    ip_address = fields.Char(string="IP Address")
    domain_name = fields.Char(string="Domain Name")
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
    tickets = fields.One2many("emdad.support", "related_subscription", string="Tickets")
    status_char = fields.Char(string="Status (Char)", compute="_compute_status_char", store=True, readonly=True)
    server_created = fields.Boolean(string="Server Created")
    server_log = fields.One2many("emdad.server.log", "related_subscription", string="Log")
    restarted = fields.Boolean(string="Restarted")
    running = fields.Boolean(string="Running")
    stopped = fields.Boolean(string="Stopped")
    def create_server(self):
        for record in self:
            record.server_created = True
            record.plan = 'nano'
            server_name = record.name
            aws_access_key_id = 'AKIAX7A7NBVMJWLVM6BX'
            aws_secret_access_key = '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'
            region_name = 'eu-central-1'

            snapshot_name = 'emdad-erp-1704555745'
            instance_name = server_name
            instance_plan = 'small_3_0'

            lightsail = boto3.client('lightsail', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

            snapshot = self.get_snapshot_by_name(lightsail, snapshot_name)

            if snapshot:
                response = lightsail.create_instances_from_snapshot(
                    instanceNames=[instance_name],
                    availabilityZone=region_name + 'a', 
                    instanceSnapshotName=snapshot['name'],
                    bundleId=instance_plan,
                    tags=[
                        {
                            'key': 'Name',
                            'value': instance_name
                        }
                    ]
                )
                record.ip_address = 'created'
                
                print(f"Server created successfully from snapshot: {snapshot['name']}")
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'Emdad Created',
                        'message' : f"Server created successfully from snapshot: {snapshot['name']}"
                    }
                    created_log = logs.create(data_to_copy)
            else:
                print(f"Snapshot with name '{snapshot_name}' not found.")
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'ERROR Emdad Created',
                        'message' : f"Snapshot with name '{snapshot_name}' not found."
                    }
                    created_log = logs.create(data_to_copy)

    def get_snapshot_by_name(self, lightsail, snapshot_name):
        snapshots = lightsail.get_instance_snapshots()
        print("Snapshots Response:", snapshots)
        for snapshot in snapshots['instanceSnapshots']:
            if snapshot['name'] == snapshot_name:
                return snapshot
            for record in self:
                record.ip_address = 'hello'
        return None

    def reboot_instance(self):
        for record in self:
            instance_name = record.name

            aws_access_key_id = 'AKIAX7A7NBVMJWLVM6BX'
            aws_secret_access_key = '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'
            region_name = 'eu-central-1'

            lightsail = boto3.client('lightsail', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

            try:
                response = lightsail.reboot_instance(instanceName=instance_name)
                # record.update = f"Reboot request sent for instance: {instance_name}"
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'Server Restarted',
                        'message' : f"Reboot request sent for instance: {instance_name}"
                    }
                    created_log = logs.create(data_to_copy)
                    log.restarted = True
                    log.running = False
            except Exception as e:
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'ERROR Server Restarted',
                        'message' : f"Error rebooting instance {instance_name}: {e}"
                    }
                    created_log = logs.create(data_to_copy)
    def stop_instance(self):
        for record in self:
            instance_name = record.name  # Adjust this according to your model structure

            aws_access_key_id = 'AKIAX7A7NBVMJWLVM6BX'
            aws_secret_access_key = 'uFZJQPsRQGDWKbmJXAZgvlVwqOdoqokTL1tL087V'
            region_name = 'eu-central-1'

            # Create a Lightsail client
            lightsail = boto3.client('lightsail', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

            # Stop the instance
            try:
                response = lightsail.stop_instance(instanceName=instance_name, force=False)
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'ERROR Server Stopped',
                        'message' : f"Stop request sent for instance: {instance_name}"
                    }
                    created_log = logs.create(data_to_copy)
                    log.stopped = True
                    log.running = False
            except Exception as e:
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'ERROR Server Stopped',
                        'message' : f"Error stopping instance {instance_name}: {e}"
                    }
                    created_log = logs.create(data_to_copy)
    def start_instance(self):
        for record in self:
            instance_name = record.name  # Adjust this according to your model structure

            aws_access_key_id = 'AKIAX7A7NBVMJWLVM6BX'
            aws_secret_access_key = 'uFZJQPsRQGDWKbmJXAZgvlVwqOdoqokTL1tL087V'
            region_name = 'eu-central-1'

            lightsail = boto3.client('lightsail', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

            try:
                response = lightsail.start_instance(instanceName=instance_name)
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'Server Started',
                        'message' : f"Start request sent for instance: {instance_name}"
                    }
                    created_log = logs.create(data_to_copy)
                    log.stopped = False
                    log.running = True
            except Exception as e:
                logs = self.env['emdad.server.log']
                for log in self:
                    data_to_copy = {
                        'related_subscription' : log.id,
                        'status' : 'Server Started',
                        'message' : f"Error starting instance {instance_name}: {e}"
                    }
                    created_log = logs.create(data_to_copy)
    @api.depends("status")
    def _compute_status_char(self):
        for record in self:
            record.status_char = dict(record._fields["status"].selection).get(record.status, "")

    @api.depends('start_date')
    def _compute_subscription_id(self):
        for record in self:
            if record.start_date:
                year_month = record.start_date.strftime('%Y%m')
            else:
                year_month = '000000'
            
            subscription_id = f"EMDAD{year_month}{record.id}"
            record.name = subscription_id

    @api.depends('next_renewal')    
    def _calculate_days_until_renewal(self):
        for record in self:
            if record.next_renewal:
                today = datetime.now().date()
                remaining_days = (record.next_renewal - today).days
                record.days_until_renewal = remaining_days
            else:
                record.days_until_renewal = 0.0

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

class EmdadSupport(models.Model):
    _name="emdad.support"
    
    name = fields.Char(string="Name", compute="_ticket_id")
    type = fields.Selection([('technical','Technical'), ('billing','Billing'), ('general','General')], string="Ticket Type")
    medium = fields.Selection([('email','Email'), ('phone','Phone'), ('inspection','Inspection')], string="Ticket Medium")
    related_to = fields.Selection([('aws','Amazon Web Services'), ('system','System')])
    subject = fields.Char(string="Subject")
    issue = fields.Text(string="Issue Explained")
    status = fields.Selection([('new','New'), ('progress','Progress'), ('solved','Solved'), ('cancel','Cancel')], string="Status", default="new")
    assigned_to = fields.Many2one("emdad.hr", string="Assigned Employee")
    related_subscription = fields.Many2one("emdad.customer", string="Subscription")
    contact_name = fields.Char(string="Contact Name", related="related_subscription.contact_name")
    contact_email = fields.Char(string="Contact Email", related="related_subscription.email")
    contact_phone = fields.Char(string="Contact Phone", related="related_subscription.phone")
    sub_status = fields.Selection([('new','New'),('active','In Progress'), ('expired','Expired')], string="Status", related="related_subscription.status")
    start_date = fields.Datetime(string="Started On")
    finish_date = fields.Datetime(string="Finished On")
    status_char = fields.Char(string="Status (Char)", compute="_compute_status_char", store=True, readonly=True)

    @api.depends("status")
    def _compute_status_char(self):
        for record in self:
            record.status_char = dict(record._fields["status"].selection).get(record.status, "")

    def close_ticket(self):
        for record in self:
            record.status = 'solved'
            record.finish_date = fields.Datetime.now()
    def start_ticket(self):
        for record in self:
            record.status = 'progress'
            record.start_date = fields.Datetime.now()
    @api.depends('related_subscription', 'create_date')
    def _ticket_id(self):
        for record in self:
            if record.related_subscription and record.create_date:
                subscription_id = record.related_subscription.id
                ticket_id = f"ISSUE{subscription_id}{record.id}"
                record.name = ticket_id
            else:
                record.name = 'NOT DEFINED'

class EmdadServerLog(models.Model):
    _name="emdad.server.log"

    name = fields.Char(string="Log ID")
    related_subscription = fields.Many2one("emdad.customer", string="Related Subscription")
    status = fields.Char(string="Status")
    message = fields.Text(string="Message")