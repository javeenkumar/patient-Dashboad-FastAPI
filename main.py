from fastapi import FastAPI, Path, Query
import json

app = FastAPI(
    title="Patient Dashboard",
    description='This dashboard used to manage patient record',
    )

# Load Json File 
def loadJson():
    with open('patients.json','r')as f:
        data = json.load(f)
    return data

# Used Get Method 
@app.get('/')
def home():
    return{'message':'Wellcome to Dashboad'}

@app.get('/List Patient')
def viewList():
    return loadJson()

# Path Parameter
@app.get('/search/{patient_id}',description='Search By Id')
def search_Patient_by_ID(patient_id:str = Path(..., title= 'ID')):
    if patient_id not in loadJson():
        return {'message':'Invalid Id'}
    else:
        return loadJson()[patient_id]

# Query Parameter
@app.get('/sort')
def Sort_Patient(
    doctorname: str |None = Query(None, description="Filter by Doctor"),
    address: str |None = Query(None, description="Filter by Address"),
    admitdate: str |None = Query(None, description="Filter by Admit Date")
    ):
    data = loadJson()

    result = {}
    for patient_id, patient in data.items():
        
        if doctorname and patient.get('doctor') != doctorname:
            continue

        if address and patient.get("address") != address:
            continue

        if admitdate and patient.get("admit_date") != admitdate:
            continue

        result[patient_id] = patient

    return result
 