'''
Reference Document Type: Site Survey
'''

user = frappe.session.user
   
if user in ["Administrator", "manisha.sadbhavrenewable@gmail.com", "mp@sadbhavrenewables.com", "prachidubey0409@gmail.com", "tara.sadbhavrenewable@gmail.com", "ergayatrisadbhav01@gmail.com", "daminisadbhavrenewable7@gmail.com"]:
    conditions = ""  # Can see all quotations
else:
    conditions = f"`tabSite Survey`.`_assign` LIKE '%{user}%' OR `tabSite Survey`.`surveyed_by` = '{user}' OR `tabSite Survey`.`owner` = '{user}'"