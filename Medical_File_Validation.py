import pandas as pd
import os
import pymssql
from datetime import datetime
import time
import easygui
import math

print('This executable is used to evaluate medical datasets. Currently, this program only works files with column '
      'headers in the first row.')
print("")
print("Instructions:")
print("-First, provide the file path to the file")
print('-Next, provide the file name')
print('-Provide your sg user name (sg credentials are used for validating ICD and CPT codes in database)')
print('-Provide your sg password')
print('And as always, please close the program or press "enter" when the program is complete')
print("")


pathname = input('Where is the file located?')
filename = input('What is the filename?')

sg_username = input("What is your sg username? (i.e. sglastname): ")
sg_password = easygui.passwordbox("What is your sg password: ")
sg_password = str(sg_password)

print("")
print("")
print("How is this file delimited?")
print("Please choose one of the following options with a number...")
print("")
print("     1) TXT file - Tab")
print('     2) TXT file - Pipe ("|")')
print('     3) TXT file - Comma (",")')
print('     4) CSV file - Comma (",")')
print("     5) XLSX file")
print("")
option_type = input('Which option would you like?')
# option_type = '1'
str(option_type)

os.chdir(pathname)


#What is the format of the medical data file?

if option_type == '1':
    option_type = 'txt'
    file = pd.read_csv(filename, index_col=0, sep='\t')
elif option_type == '2':
    option_type = 'txt'
    file = pd.read_csv(filename, index_col=0, sep='|')
elif option_type == '3':
    option_type = 'txt'
    file = pd.read_csv(filename, index_col=0, sep=',')
elif option_type == '4':
    option_type = 'csv'
    file = pd.read_csv(filename, index_col=0)
elif option_type == '5':
    option_type = 'xlsx'
    file = pd.read_excel(filename, index_col=0)
else:
    input("Invalid response. Hit Enter to exit.")


#original data frame basically
orgfile = file



#Start timer for performance
From = time.time()


print('Step 1 of 5: Storing CPTS and ICDs for comparision......')

#SSMS connection

c = pymssql.connect(server='SQL.com', user='PROD\{sgusername}'.format(sgusername=sg_username), password='{sgpassword}'.format(sgpassword=sg_password), database='MEDICAL')

#Create cursor for the actual command

db_cursor = c.cursor()

#Your sql command

db_cursor.execute('''SELECT TOP 200000
                        ID
                        FROM MEDICAL.DBO.ICD''')

#Need the fetchall command to pull all rows. Storing data into table or dataframe

pulldata = db_cursor.fetchall()

icd_data = pulldata

#Another SQL command for other codes

db_cursor.execute('''SELECT TOP 50000
                        ID
                        from MEDICAL.DBO.CPT''')


pulldata2 = db_cursor.fetchall()

cpt_data = pulldata2


db_cursor.close()

#Closed connection
c.close()



#So basically, I have this program checking to see if common fields I need are in a file or not. The column names have
# a ton of variation so I originally created lists for the program to check if the column name was there, but changed
# my mind as our list will most likely grow. I decided instead of having pre-built lists, the program will rebuild them
# each time after reading the possibilities from an excel. The excel allows anyone to add to the list at anytime. Also,
# I originally started with lists and my program was super slow so I converted my lists to sets and it made a world of difference.




# dob_list = ['dob', 'dateofbirth', 'birthdate','mbrbrthdt', 'claimantdob']
# age_list = ['age', 'claimantage', 'memberage']
# rel_list = ['relationship', 'rel', 'relationshipcode', 'relcode','mbrrelcd']
# gender_list = ['gender', 'gendercode', 'sex', 'claimantgender', 'mbrrelcd']
# icd_list = ['icd10', 'icd9', 'icd', 'diagnosiscode', 'icddiagnosisid', 'primarydx', 'prindiagcd', 'diagnosis', 'diagnosisprimary']
# pos_list = ['pos', 'poscode', 'placeofservice', 'hiaaposcode','placeofservicename', 'placesrvccd']
# paiddate_list = ['paiddate', 'datepaid', 'paymentdate', 'claimpaiddate', 'paiddt', 'Paid Date']
# fromdate_list = ['datefrom', 'fromdate', 'from', 'servicebegindate', 'servicestartdate', 'srvcstrtdt', 'servicefrom', 'fromdt']
# thrudate_list = ['datethru', 'thrudate', 'thru', 'serviceenddate', 'srvcenddt', 'servicethrough', 'todt']
# claimant_list = ['claimantid', 'memberid', 'memid', 'subkey']
# cpt_list = ['cpt', 'cptcode', 'cpt4code', 'procedurecode', 'primaryprocedurecode', 'prinproccd', 'procedure']
# provider_list = ['providername', 'prov','billingprovidername']
# providerid_list = ['providerid', 'provid', 'taxid', 'taxidnbr', 'billprovtaxidkey', 'providertin']
# revcode_list = ['rev', 'revcode','revenuecode', 'rvnucd']
# paidamount_list = ['paidamount', 'paid', 'paidamt', 'totalpaidamount', 'paidamtincrd']
# chargeamount_list = ['chargedamount', 'chargeamt', 'charged']
# claimtype_list = ['claimtype', 'type', 'rectype']
# innetwork_list = ['network', 'networkindicator', 'innetworkind', 'ntwkind']
# copay_list = ['copay', 'total copay amount', 'cpayamtincrd']
# coinsurance_list = ['coinsurance', 'coinsrnamtincrd']
# deductible_list = ['deductible', 'ddctblamtincrd']



#Made sets instead of lists. Currently these are empty, however, I read an xlsx file next and the program builds
# the sets out.


#Advantage of using sets over lists?
#-Set item has an indexed position as compared to not in a list. Makes it easier to find.
#-Sets don't allow duplicates. Advantage cause looking at less data and in this case it isn't important to know how
# many times it appears.

dob_list = set()
age_list = set()
rel_list = set()
gender_list = set()
icd_list = set()
pos_list = set()
paiddate_list = set()
fromdate_list = set()
thrudate_list = set()
claimant_list = set()
cpt_list = set()
provider_list = set()
providerid_list = set()
revcode_list = set()
paidamount_list = set()
chargeamount_list = set()
claimtype_list = set()
innetwork_list = set()
copay_list = set()
coinsurance_list = set()
deductible_list = set()




column_repository = pd.read_excel(r'J:\MED_Column_Repository.xlsx', skiprows=5)


#Defined function for adding to the sets from the columns of the excel spreadsheet. Also, drop blanks.
def ls(u, y):

    for x in column_repository[u].dropna():
        y.add(x)


#Calling function to go to this column name and adding the list/set items.

ls('DateofBirth', dob_list)
ls('Age', age_list)
ls('Relationship', rel_list)
ls('Gender', gender_list)
ls('ICD', icd_list)
ls('POS', pos_list)
ls('PaidDate', paiddate_list)
ls('FromDate', fromdate_list)
ls('ThruDate', thrudate_list)
ls('Claimant', claimant_list)
ls('CPT', cpt_list)
ls('Provider', provider_list)
ls('ProviderID', providerid_list)
ls('RevCode', revcode_list)
ls('PaidAmount', paidamount_list)
ls('ChargeAmount', chargeamount_list)
ls('ClaimType', claimtype_list)
ls('InNetwork', innetwork_list)
ls('Copay', copay_list)
ls('Coinsurance', coinsurance_list)
ls('Deductible', deductible_list)





project_requirements = []


print('Step 2 of 5: Evaluating column names for comparision......')


#Now this step is determining if the columns I'm looking for are actually there and renaming them in the temporary
# tables for standardization and for additional checks later.


#Add to project requirements list if there.

def add(x):
    project_requirements.append(x)


for columns in file:
    x = str(columns)

    #lower case to reduce variations of what column could be
    x = x.lower()

    #remove symbols to reduce variation.
    x = ''.join(a for a in x if a not in " '\"_-/.,")

#dob


#if the name of the column is not one of the possible column names for DOB then ignore else add it to project
    # requirements list
    if x not in dob_list:
        pass
    else:
        add("DOB")

        #rename dataframe column for later reference
        file.rename(columns={columns: 'DOB'}, inplace=True)

#age

    if x not in age_list:
        pass
    else:
        add("Age")
        file.rename(columns={columns: 'Age'}, inplace=True)

#relationship

    if x not in rel_list:
        pass
    else:
        add("Relationship")
        file.rename(columns={columns: 'Relationship'}, inplace=True)
#gender

    if x not in gender_list:
        pass
    else:
        add("Gender")
        file.rename(columns={columns: 'Gender'}, inplace=True)
#icd

    if x not in icd_list:
        pass
    else:
        add("ICD")
        file.rename(columns={columns: 'ICD'}, inplace=True)

#pos

    if x not in pos_list:
        pass
    else:
        add("POS")
        file.rename(columns={columns: 'POS'}, inplace=True)
#paid date

    if x not in paiddate_list:
        pass
    else:
        add("PaidDate")
        file.rename(columns={columns: 'PaidDate'}, inplace=True)
#date from

    if x not in fromdate_list:
        pass
    else:
        add("DateFrom")
        file.rename(columns={columns: 'DateFrom'}, inplace=True)

#date thru

    if x not in thrudate_list:
        pass
    else:
        add("DateThru")
        file.rename(columns={columns: 'DateThru'}, inplace=True)

#claimant id

    if x not in claimant_list:
        pass
    else:
        add("ClaimantID")
        file.rename(columns={columns: 'ClaimantID'}, inplace=True)

#cpt

    if x not in cpt_list:
        pass
    else:
        add("CPT")
        file.rename(columns={columns: 'CPT'}, inplace=True)

#provider name

    if x not in provider_list:
        pass
    else:
        add("ProviderName")
        file.rename(columns={columns: 'Providername'}, inplace=True)

#provider id

    if x not in providerid_list:
        pass
    else:
        add("ProviderID")
        file.rename(columns={columns: 'ProviderID'}, inplace=True)

#rev code

    if x not in revcode_list:
        pass
    else:
        add("RevCode")
        file.rename(columns={columns: 'RevCode'}, inplace=True)

#paid amount

    if x not in paidamount_list:
        pass
    else:
        add("PaidAmount")
        file.rename(columns={columns: 'PaidAmount'}, inplace=True)
#charged amount

    if x not in chargeamount_list:
        pass
    else:
        add("ChargeAmount")
        file.rename(columns={columns: 'ChargeAmount'}, inplace=True)

#claim type

    if x not in claimtype_list:
        pass
    else:
        add("ClaimType")
        file.rename(columns={columns: 'ClaimType'}, inplace=True)

#network

    if x not in innetwork_list:
        pass
    else:
        add("Network")
        file.rename(columns={columns: 'Network'}, inplace=True)

#copay

    if x not in copay_list:
        pass
    else:
        add("Copay")
        file.rename(columns={columns: 'Copay'}, inplace=True)
#coinsurance

    if x not in coinsurance_list:
        pass
    else:
        add("Coinsurance")
        file.rename(columns={columns: 'Coinsurance'}, inplace=True)

#Deductible

    if x not in deductible_list:
        pass
    else:
        add("Deductible")
        file.rename(columns={columns: 'Deductible'}, inplace=True)



#Now, I'm comparing a list of the columns I know I have compared to the list I know that I need. This is why I
# renamed columns to see if I have a match.

minimum_requirements = ['DOB', 'Age', 'Relationship', 'Gender', 'POS', 'DateFrom', 'DateThru', 'PaidDate', 'Copay', 'Coinsurance',
                        'Deductible', 'Network', 'PaidAmount', 'ChargeAmount', 'ClaimType', 'RevCode', 'CPT',
                        'ProviderName', 'ProviderID', 'ClaimantID', 'ICD']

#This is where I find columns missing. Subtracting the lists

actual_columns_received = list(set(minimum_requirements) - set(project_requirements))


print('Step 3 of 5: Moving to CPT and ICD evaluation.......')


#Since I also have the column names standardized, I'm also trying to see the unique values in each column. Else
# printing that it "Can't find the column".

try:
    relunique = file.Relationship.unique()
except:
    relunique = 'Can\'t find column'

try:
    genderunique = file.Gender.unique()
except:
    genderunique = 'Can\'t find column'

try:
    ageunique = file.Age.unique()
except:
    ageunique = 'Can\'t find column'

try:
    networkunique = file.Network.unique()
except:
    networkunique = 'Can\'t find column'

try:
    posunique = file.POS.unique()
except:
    posunique = 'Can\'t find column'

try:
    paiddate = str(file['Paid Date'])
except:
    paiddate = 'Can\'t find column'

try:
    paiddate = file.PaidDate.unique()
except:
    paiddate = 'Can\'t find column'




#Verifying ICD codes against sql database or saved query/dataframe from earlier.


str_icd = set()

#Adding fields to a set to check if they exist. This is adding fields from sql to set

for q in icd_data:
    q = str(q)
    q = ''.join(h for h in q if h not in " '_-/.,")
    q = q.replace(")", "")
    q = q.replace("(", "")
    str_icd.add(q)


#Cleaning ICD column in file/dataframe to compare against. Also, totaling up how many icd coedes are
# found to be correct.

try:
    icd_column = file['ICD']
except:
    icd_column = ["Error: Can\'t find"]

try:
    icd_column_na_1 = file['ICD'].dropna()
except:
    icd_column_na_1 = ["Error: Can\'t find"]

try:
    icd_column_na = len(icd_column) - len(icd_column_na_1)
except:
    icd_column_na = ["Error: Can\'t find"]




icd_column_na_1 = icd_column_na_1

icd_valid = set()


#This is the column from the medical file named icd column minus NA as shown in try statement above.

for z in icd_column_na_1:
    z = str(z).upper()
    z = ''.join(h for h in z if h not in " '_-/.,")
    icd_valid.add(z)


#Checking for codes that exist in each list as they are matches.

icd_matched = set(icd_valid).intersection(str_icd)


num_icd_valid = len(icd_valid)


icd_valid_count = len(icd_matched)


#Getting numbers later for logging....number of valid codes/total codes...how many rows...how many columns
# for summary file

rows = file.shape[0]
shcolumns = file.shape[1]




#Everything I did above for icd codes is being done for CPT codes. Including making sets and comparing what
# the database has compared to what is in the file.

str_cpt = set()


for b in cpt_data:
    b = str(b)
    b = ''.join(h for h in b if h not in " '_-/.,")
    b = b.replace(")", "")
    b = b.replace("(", "")
    str_cpt.add(b)


try:
    cpt_column = file['CPT']
except:
    cpt_column = ["Error: Can\'t find"]

try:
    cpt_column_na_1 = file['CPT'].dropna()
except:
    cpt_column_na_1 = ["Error: Can\'t find"]

try:
    cpt_column_na = (len(cpt_column) - len(cpt_column_na_1))
except:
    cpt_column_na = ["Error: Can\'t find"]



cpt_valid = set()


#Here I'm checking if the CPT code is 5 digits long...if not then it will need 0s added to make it 5 digits.

for j in cpt_column_na_1:
    j = str(j)
    j = j.upper()
    j = ''.join(k for k in j if k not in "' _-/.,")
    if len(j) == 5:
        cpt_valid.add(j)

    elif len(j) == 4:
        j = '0' + j
        cpt_valid.add(j)

    elif len(j) == 3:
        j = '00' + j
        cpt_valid.add(j)

    elif len(j) == 2:
        j = '000' + j
        cpt_valid.add(j)


    elif len(j) == 1:
        j = '0000' + j
        cpt_valid.add(j)

    else:
        j = '00000'
        cpt_valid.add(j)


#Compaing the sets of the database vs file to see matches

cpt_matched = set(cpt_valid).intersection(str_cpt)

#How many matches?

num_cpt_valid = len(cpt_valid)



cpt_valid_count = len(cpt_matched)

cpt_valid_count = round(cpt_valid_count, 1)


#Take the number of matched vs total and make percentage


icd_valid_per = (icd_valid_count/num_icd_valid)*100
cpt_valid_per = round((cpt_valid_count/num_cpt_valid), 2)*100



print('Step 4 of 5: Reading paid dates to determine missing year/months......')



#Reviewing Paid Dates. Reading the whole dataframe basically as a string.


file = file.astype(str)

#Checking the paid dates that exist in a file. Mostly interested in just getting a year/month information to see what
# is there and know what is missing immediately.

try:
    file['PaidAgain'] = pd.to_datetime(file['PaidDate'])
except:
    file['PaidAgain'] = file['PaidDate']


try:
    file['PaidAgain'] = file['PaidAgain']
except:
    file['PaidAgain'] = 'Can\'t find column'


try:
    file['Month'] = file['PaidAgain'].dt.month
except:
    file['Month'] = 'Can\'t find column'


paidcheck = set()

try:
    for v in file['Month']:
        paidcheck.add(v)
except:
    pass

try:

    if len(set(paidcheck)) == 1:
        file['PaidFix'] = file['PaidAgain']
        file['YRMTH2'] = file['PaidFix'].str[0:6]


except:
    pass


try:

    boo = file['YRMTH2'].unique()

except:
    pass


try:
    file['Year'] = file['PaidAgain'].dt.year
except:
    file['Year'] = 'Can\'t find column'



try:
    file['YRMTH'] = (file['Year']*100) + (file['Month'])
except:
    file['YRMTH'] = 'Can\'t find column'

try:
    file['YRMTH'] = file['YRMTH']
except:
    pass


try:
    unique = file['YRMTH'].unique()
except:
    unique = 'Can\'t find column'

sub = 'Can\'t find column'

null_before = len(file['YRMTH'])


#Getting rid of nulls from year month. Was having some issues with file variation so made some backup checks in
# case all nulls returned.

null_after = file['YRMTH'].dropna()
null_after = len(file['YRMTH'])


null_dates = null_before - null_after



dateset = set()


for dates in file['YRMTH'].dropna():
    dateset.add(dates)

#Start Summary File


#Define write as function
def w(x):
    summary_file.write(x)

#Define new line
def n():
    summary_file.write('\n')

os.chdir(pathname)

#Taking just filename of the file and adding Summary to the front of it for a new file.
revised_filename = os.path.splitext(filename)[0]


summary_file = open('Summary - ' + revised_filename + '.txt', 'w')

orgfile_columns = str(orgfile.columns)

print('Step 5 of 5: Creating Data Forecast file......')


#w = write to summary file
#n = newline

w('------------------------------DATA FORECAST------------------------------')
n()
n()
w('This is an approximation of your data file and how well it will be processed. For quality assurance, please continue'
  ' to follow proper procedure' + '\n'
  ' when evaluating your data.')
n()
n()
w('**Column list:')
n()
n()
w(orgfile_columns)
n()
n()
w('**Number of Columns: ' + str(shcolumns))
n()
w('**Number of Rows: ' + str(rows))
n()
n()
w('**ICD Valid Codes: ' + str(icd_valid_per) + '%')
n()
w('**Blank ICD Rows: ' + str(round((icd_column_na/len(icd_column)*100), 2)) + '%')
n()
w('**CPT Valid Codes: ' + str(cpt_valid_per) + '%')
n()
w('**Blank CPT Rows: ' + str(round((cpt_column_na/len(cpt_column)*100), 2)) + '%')
n()
n()
w('**Missing Columns: ')
n()
n()
for field in actual_columns_received:
    w(field + '\n')
if len(actual_columns_received) == 0:
    w("Data is of a high compliance. No fields appear to be missing." + '\n')
else:
    pass
n()
w('**Year/Month of Paid Dates: ')
n()
n()
sub = 'column'
w(str(sorted(dateset)))
n()
w('Back up Paid Date Logic:')
n()

#Sort paid dates basically chronologically

try:
    w(str(sorted(boo)))
except:
    pass
n()
n()
w('Number of Null Paid Dates: ' + str(null_dates))
n()
if len(dateset) < 12:
    w('***Data appears to have LESS than 12 months of data')
else:
    w('***Data appears to have 12 or more months of data')
n()
n()
w('**POS Codes: ')
n()
n()
w(str(posunique))
n()
n()
w('**Relationship Codes: ')
n()
n()
w(str(relunique))
n()
n()
w('**Gender Codes: ')
n()
n()
w(str(genderunique))
n()
n()
w('**Network Codes: ')
n()
n()
w(str(networkunique))
n()
n()
w('---------------------------COLUMN REPOSITORY---------------------------')
n()
n()
w('This program is currently able to evaluate the following column headers with some variation. If their are additional'
  ' column headers that you\'d like to be evaluated in the future,' + '\n'
  ' please email a department Python SME.')
n()
n()
w(str(dob_list))
n()
w(str(age_list))
n()
w(str(rel_list))
n()
w(str(gender_list))
n()
w(str(icd_list))
n()
w(str(pos_list))
n()
w(str(paiddate_list))
n()
w(str(fromdate_list))
n()
w(str(thrudate_list))
n()
w(str(claimant_list))
n()
w(str(cpt_list))
n()
w(str(provider_list))
n()
w(str(providerid_list))
n()
w(str(revcode_list))
n()
w(str(paidamount_list))
n()
w(str(chargeamount_list))
n()
w(str(claimtype_list))
n()
w(str(innetwork_list))
n()
w(str(copay_list))
n()
w(str(coinsurance_list))
n()
w(str(deductible_list))
n()
print('')


#How long did the program take to run.
To = time.time()
laptime = round(To - From, 2)
minutes = round(laptime/60, 1)
strminutes = str(minutes)
print('I rock....that only took me ' + strminutes + ' minutes!')



















