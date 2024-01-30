from emdad import fields, api, models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from emdad.exceptions import ValidationError
from geopy.geocoders import Nominatim  # Import the geopy library

class EmdadHR(models.Model):
    _name="emdad.hr"

    name = fields.Char(string="Employee Name")
    emp_id = fields.Integer(string="Employee ID")
    emdad_id = fields.Integer(string="Emdad ID")
    emdad_user = fields.Many2one("res.users", related="active_contract.emdad_user",string="Related User")
    related_company = fields.Many2one("res.company", related="active_contract.related_company", string="Related Company")
    #basic Information
    image = fields.Binary(string="Image")
    phone = fields.Char(string="Phone Number", Unique=True)
    building = fields.Char(string="Building")
    street = fields.Char(string="Street Name")
    city = fields.Many2one("res.country.state", string="City")
    country = fields.Many2one("res.country", string="Country")
    personal_email = fields.Char(string="Personal Email")
    #personal information
    dob = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_get_age")
    id_type = fields.Selection([('national','National ID'), ('passport','Passport'),('iqama','Iqama')], string="Indentification Type")
    document_id = fields.Char(string="Document ID", Unique=True)
    document = fields.Binary(string="ID Copy")
    expiary = fields.Date(string="Expiary Date")
    doc_status = fields.Selection([('not','Not Active'), ('active','Active')], string="Document Status", compute="_doc_status")
    nationality = fields.Many2one("res.country", string="Nationality")
    gosi_number = fields.Char(string="GOSI #")
    gosi_issue = fields.Date(string="GOSI Issuance")

    cv = fields.Binary(string="CV")
    #education
    education = fields.One2many("emdad.hr.education", "related_employee", string="Education")
    #work history
    work = fields.One2many("emdad.hr.work.history", "related_employee", string="Work History")
    years = fields.Float(string="Experience(Years)", compute="_get_experience")
    status = fields.Selection([('active','Active Employee'), ('not','Not Active')], string="Employee Status")
    contracts = fields.One2many("emdad.hr.contract", "related_employee", string="Contracts")

    #work information
    active_contract = fields.Many2one("emdad.hr.contract", string="Active Contract")
    position = fields.Many2one("emdad.hr.position", related="active_contract.job")
    end_date = fields.Date(string="Valid Till", related="active_contract.end_date" )
    department = fields.Many2one("emdad.hr.department", related="active_contract.related_department", string="Department")
    manager = fields.Many2one("emdad.hr", related="active_contract.related_manager")
    salary = fields.Float(string="Salary", related="active_contract.total_salary")



    @api.onchange('doc_status', 'status')
    def deactivate_profile(self):
        for record in self:
            if record.status == 'active':
                if record.doc_status == 'not':
                    record.status = 'not'
                else:
                    record.status = 'active'
            else:
                record.status = 'not'
    def status_inactive(self):
        for record in self:
            record.status = 'not'
    def status_active(self):
        for record in self:
            record.status = 'active'
    @api.depends('work')
    def _get_experience(self):
        for record in self:
            if record.work:
                record.years = sum(line.experience_years for line in record.work)
            else:
                record.years = 0
    @api.depends('expiary')
    def _doc_status(self):
        for record in self:
            if record.expiary:
                if record.expiary < datetime.now().date():
                    record.doc_status = 'not'
                elif record.expiary == datetime.now().date():
                    record.doc_status = 'not'
                else:
                    record.doc_status = 'active'
            else:
                record.doc_status = 'active'


    @api.depends('dob')
    def _get_age(self):
        for record in self:
            if record.dob:
                dob = record.dob
                today = datetime.now().date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                record.age = age
            else:
                record.age = 0



class EmdadHRDepartment(models.Model):
    _name="emdad.hr.department"

    name = fields.Char(string="Department Name")
    parent_department = fields.Many2one("emdad.hr.department", string="Parent Department")
    manager = fields.Many2one("emdad.hr", string="Manager")
    employees = fields.One2many("emdad.hr", "department", string="Employees")


class EmdadHREducation(models.Model):
    _name="emdad.hr.education"

    name = fields.Char(string="Related ID")
    major = fields.Many2one("emdad.hr.education.major", string="Major")
    school = fields.Many2one("emdad.hr.education.school", string="School")
    country = fields.Many2one("res.country", string="Country")
    graduation_year = fields.Date(string="Graduation Year")
    certificate = fields.Binary(string="Certificate")
    related_employee = fields.Many2one("emdad.hr", string="Related Employee")

class EmdadHREducationMajor(models.Model):
    _name="emdad.hr.education.major"

    name = fields.Char(string="Major")

class EmdadHREducationSchool(models.Model):
    _name="emdad.hr.education.school"

    name = fields.Char(string="School")

class EmdadHRWorkHistory(models.Model):
    _name="emdad.hr.work.history"

    name = fields.Char(string="Company Name")
    from_date = fields.Date(string="From Date")
    till_date = fields.Date(string="End Date")
    departure_reason = fields.Selection([('resigned','Resigned'), ('fired','Fired'), ('promotion','Promoted')], string="Departure Reason")
    position = fields.Char(string="Position")
    description = fields.Text(string="Job Description")
    salary = fields.Float(string="Salary")
    related_employee = fields.Many2one("emdad.hr", string="Related Employee")
    experience_years = fields.Integer(string="Experience Years", compute="_compute_experience")

    @api.onchange('till_date')
    def alert_older_than_today(self):
        for record in self:
            if record.till_date:
                if record.till_date > date.today():
                    raise ValidationError("You can not assign a date older than the current date")
            else:
                record.till_date = date.today()

    @api.depends('from_date', 'till_date')
    def _compute_experience(self):
        for record in self:
            if record.from_date and record.till_date:
                delta = relativedelta(record.till_date, record.from_date)
                record.experience_years = delta.years
            else:
                record.experience_years = 0
  
class EmdadHRContracts(models.Model):
    _name = "emdad.hr.contract"

    name = fields.Char(string="Contract ID")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    related_employee = fields.Many2one("emdad.hr", string="Related Employee")
    contract_type = fields.Selection([('full', 'Full Time'), ('part','Part Time'), ('consult', 'Consultant')], string="Contract Type")
    contract_content = fields.Html(string="Contract Details")
    job = fields.Many2one("emdad.hr.position", string="Job Position")
    related_department = fields.Many2one("emdad.hr.department", related="job.department", string="Department")
    related_manager = fields.Many2one("emdad.hr", related="job.department.manager", string="Manager")
    description = fields.Html(string="Job Description", related="job.description")
    status = fields.Selection([('not', 'Expired Contract'), ('active','Active'), ('stop','Terminated')], string="Contract Status", default="not")
    salary = fields.One2many("emdad.hr.salary", "related_contract", string="Salary")
    total_salary = fields.Float(string="Assigned Salary", compute="_compute_salary")
    work_days = fields.One2many("emdad.hr.work", 'related_contract', string="Work Days")
    total_hours = fields.Float(string="Total Hours / Week", compute="_get_hours")
    over_time = fields.Selection([('no','No Overtime'),('can','Overtime Without Approval'),('approval','Overtime With Approval')], string="Overtime Status")
    bank = fields.Many2one("emdad.hr.bank", string="Bank Information")
    emdad_user = fields.Many2one("res.users", string="Emdad User")
    related_company = fields.Many2one("res.company", string="Related Company")
    #rules
    rules = fields.One2many("emdad.hr.user", "related_contract", string="Rules")
    @api.depends('work_days')
    def _get_hours(self):
        for record in self:
            if record.work_days:
                record.total_hours = sum(line.working_hours for line in record.work_days)
            else:
                record.total_hours = 0

    @api.depends('salary')
    def _compute_salary(self):
        for record in self:
            if record.salary:
                record.total_salary = sum(line.amount for line in record.salary)
            else:
                record.total_salary = 0
    @api.onchange('start_date','end_date','status')
    def _contract_status(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < date.today():
                    record.status = 'not'
                elif record.end_date == date.today():
                    record.status = 'not'
                else: 
                    record.status = 'active'
            else:
                record.status = 'not'

class EmdadUserRules(models.Model):
    _name="emdad.hr.user"

    name = fields.Char(string="Rule")
    app = fields.Many2one("ir.model", string="Application")
    view = fields.Boolean(string="View")
    read_app = fields.Boolean(string="Read")
    write = fields.Boolean(string="Write")
    edit = fields.Boolean(string="Edit")
    related_contract = fields.Many2one("emdad.hr.contract", string="Contract")
    related_employee = fields.Many2one("emdad.hr", related="related_contract.related_employee", string="Related Employee")
    related_user = fields.Many2one("res.users", related="related_contract.related_employee.emdad_user", string="User")
    
class EmdadHRBank(models.Model):
    _name="emdad.hr.bank"

    name = fields.Char(string="Account Number")
    bank = fields.Char(string="Bank Name")
    iban = fields.Char(string="IBAN")
    related_contract = fields.Many2one("emdad.hr.contract", string="Related Contract")
    related_employee = fields.Many2one("emdad.hr", related="related_contract.related_employee", string="Related Employee")

class EmdadWorkDays(models.Model):
    _name="emdad.hr.work"

    name = fields.Char(string="Plan Name")
    related_contract = fields.Many2one("emdad.hr.contract", string="Related Contract")
    related_employee = fields.Many2one("emdad.hr", related="related_contract.related_employee", string="Employee")
    day = fields.Selection([('1','Sunday'),('2','Monday'),('3','Tuesday'), ('4','Wednesday'),('5','Thursday'),('6','Friday'),('7','Saturday')])
    start = fields.Float(string="Start From")
    break_time = fields.Float(string="Break")
    end = fields.Float(string="End Time")
    working_hours = fields.Float(string="Working Hours", compute="_compute_working_hours", store=True)   

    @api.depends('start', 'break_time', 'end')
    def _compute_working_hours(self):
        for record in self:
            start_time = record.start
            end_time = record.end
            break_time = record.break_time
            working_hours = end_time - start_time - break_time
            record.working_hours = max(working_hours, 0)

class EmdadHRSalary(models.Model):
    _name="emdad.hr.salary"

    name = fields.Char(string="Payroll ID", compute="_payroll_item")
    related_contract = fields.Many2one("emdad.hr.contract", string="Related Contract")
    related_employee = fields.Many2one("emdad.hr", related="related_contract.related_employee")
    structure = fields.Selection([('basic','Basic'),('medical','Medical Allowance'),('special','Special Allowance'), ('dearness','Dearness Allowance'), ('rent','House Rent'), ('convey','Conveyance Allowance'), ('deduction', 'Deduction')], string="Structure")
    deduction = fields.Selection([('pro','Professional Tax'), ('source','Tax Deduct at Source'), ('epf','EPF'),('health','Health Insurance')], string="Deduction")
    amount = fields.Float(string="Amount")
    attendance = fields.Boolean(string="Attendance Effect")

    @api.depends('deduction','structure')
    def _payroll_item(self):
        for record in self:
            structure_display = record.structure
            if record.structure and record.deduction:
                if isinstance(structure_display, str):
                    record.name = (structure_display + '/' + record.deduction).upper()
                else:
                    record.name = 'Undefined Salary Structure'
            elif record.structure != 'deduction':
                record.deduction = False
                if isinstance(structure_display, str):
                    record.name = structure_display.upper()
                else:
                    record.name = 'Undefined Salary Structure'
            else:
                record.name = 'Undefined Salary Structure'
    @api.onchange('structure', 'deduction')
    def deducation_add(self):
        for record in self:
            if record.structure == 'deduction': 
                record.amount = -abs(record.amount)
            else:
                record.amount = abs(record.amount)
class EmdadJobPositions(models.Model):
    _name="emdad.hr.position"

    name = fields.Char(string="Job Position")
    duties = fields.Text(string="Duties")
    description = fields.Html(string="Job Description")
    files = fields.Binary(string="Attachements")
    department = fields.Many2one("emdad.hr.department", string="Related Department")

class EmdadAttendance(models.Model):
    _name="emdad.hr.attendance"

    name = fields.Char(string="Attendance Refernce")
    related_employee = fields.Many2one("emdad.hr", string="Employee")
    related_contract = fields.Many2one("emdad.hr.contract", related="related_employee.active_contract")
    checkin = fields.Datetime(string="Check In")
    checkout = fields.Datetime(string="Check Out")
    working_hours = fields.Float(string="Working Hours", compute="_compute_working_hours", store=True)
    extra = fields.Float(string="Extra Hours")
    checkin_location = fields.Char(string="Checkin Location")
    checkout_location = fields.Char(string="Checkout Location")
    is_checkin = fields.Boolean(string="Checkedin")
    is_checkout = fields.Boolean(string="Checkedout")
    is_late = fields.Boolean(string="Late")
    day = fields.Selection([
            ('1', 'Sunday'), ('2', 'Monday'), ('3', 'Tuesday'),
            ('4', 'Wednesday'), ('5', 'Thursday'), ('6', 'Friday'), ('7', 'Saturday')
        ], default=lambda self: str((datetime.now().weekday() + 1) % 7 + 1))
    
    def record_checkin(self):
        for record in self:
            location = self._get_current_location()
            if record.related_employee:
                record.checkin = datetime.now()
                record.is_checkin = True
                record.checkin_location = location
                record.checkin = datetime.now()
            
    def record_checkout(self):
        for record in self:
            if record.checkin and record.related_employee:
                record.checkout = datetime.now()
                record.is_checkout = True
    
    @api.depends('checkin', 'checkout')
    def _compute_working_hours(self):
        for record in self:
            if record.checkin and record.checkout:
                delta = record.checkout - record.checkin
                record.working_hours = delta.total_seconds() / 3600
            else:
                record.working_hours = 0.0
    
    def _get_current_location(self):
        geolocator = Nominatim(user_agent="your_app_name")  # Replace with your app name
        try:
            location = geolocator.geocode("Your city, country")  # Replace with the desired city and country
            if location:
                return f"{location.latitude},{location.longitude}"
        except Exception as e:
            # Handle exceptions (e.g., geocoding service unavailable)
            return False
